import asyncio
import re
from dataclasses import dataclass, field


@dataclass
class Record:
    id:       int | str
    name:     str
    age:      int | str
    email:    str
    location: str


@dataclass
class InvalidRecord:
    record: dict
    errors: list[str]


@dataclass
class ChunkResult:
    chunk_id: int
    valid:    list[Record]       = field(default_factory=list)
    invalid:  list[InvalidRecord] = field(default_factory=list)


# ──────────────────────────────────────────────
# Validação
# ──────────────────────────────────────────────

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate(raw: dict) -> tuple[Record | None, list[str]]:
    errors = []

    # id
    try:
        record_id = int(raw.get("id", ""))
        if record_id <= 0:
            raise ValueError
    except (ValueError, TypeError):
        errors.append("id: deve ser um inteiro positivo")
        record_id = raw.get("id")

    # name
    name = str(raw.get("name", "")).strip()
    if not name or len(name) < 2:
        errors.append("name: obrigatório e com pelo menos 2 caracteres")

    # age
    try:
        age = int(raw.get("age", ""))
        if not (0 <= age <= 130):
            raise ValueError
    except (ValueError, TypeError):
        errors.append("age: deve ser inteiro entre 0 e 130")
        age = raw.get("age")

    # email
    email = str(raw.get("email", "")).strip()
    if not EMAIL_RE.match(email):
        errors.append("email: formato inválido")

    # location
    location = str(raw.get("location", "")).strip()
    if len(location) < 2:
        errors.append("location: obrigatório")

    if errors:
        return None, errors

    return Record(id=record_id, name=name, age=age, email=email, location=location), []


# ──────────────────────────────────────────────
# Chunking + processamento
# ──────────────────────────────────────────────

def split_into_chunks(data: list[dict], chunk_size: int) -> list[list[dict]]:
    return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]


async def process_chunk(chunk_id: int, chunk: list[dict]) -> ChunkResult:
    result = ChunkResult(chunk_id=chunk_id)

    for raw in chunk:
        record, errors = validate(raw)
        if errors:
            result.invalid.append(InvalidRecord(record=raw, errors=errors))
        else:
            result.valid.append(record)

    await asyncio.sleep(0)
    return result


async def process_json(data: list[dict], chunk_size: int = 1000) -> dict:
    """
    Ponto de entrada principal.
    Retorna um dict com:
        valid   → lista de Record prontos para a DB 
        invalid → lista de InvalidRecord com os erros
    """
    chunks = split_into_chunks(data, chunk_size)

    tasks = [
        asyncio.create_task(process_chunk(i, chunk))
        for i, chunk in enumerate(chunks)
    ]

    results: list[ChunkResult] = await asyncio.gather(*tasks)

    all_valid   = [r for res in results for r in res.valid]
    all_invalid = [r for res in results for r in res.invalid]

    print(f"[Lucas] {len(chunks)} chunk(s) processados")
    print(f"[Lucas] ✓ válidos: {len(all_valid)}  ✗ inválidos: {len(all_invalid)}")

    return {"valid": all_valid, "invalid": all_invalid}


# ──────────────────────────────────────────────
# Teste rápido
# ──────────────────────────────────────────────

if __name__ == "__main__":
    sample = [
        {"id": 1,    "name": "Ana Silva",   "age": 28, "email": "ana@example.com",    "location": "Lisboa"},
        {"id": 2,    "name": "João Costa",  "age": 35, "email": "joao@example.com",   "location": "Porto"},
        {"id": -1,   "name": "X",           "age": "NaN", "email": "not-an-email",    "location": ""}, 
        {"id": 3,    "name": "Maria Lopes", "age": 22, "email": "maria@outlook.com",  "location": "Faro"},
        {"id": "??", "name": "",            "age": 999, "email": "bad@",              "location": "Braga"},  
    ]

    result = asyncio.run(process_json(sample, chunk_size=2))

    print("\n— Válidos —")
    for r in result["valid"]:
        print(" ", r)

    print("\n— Inválidos —")
    for r in result["invalid"]:
        print(f"  {r.record} → {r.errors}")