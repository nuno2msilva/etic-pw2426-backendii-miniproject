
from fastapi import FastAPI

from .db import Base, Record, SessionLocal, engine
from .processing import process_json


app = FastAPI()


@app.post("/json")
async def read_json(json_data: list[dict], chunk_size: int = 1000):
    """
    Endpoint to receive a list of JSON objects, process them in chunks,
    validate, and return valid and invalid records.
    """
    result = await process_json(json_data, chunk_size)

    session = SessionLocal()
    try:
        for r in result["valid"]:
            session.add(Record(name=r.name, age=r.age, email=r.email, location=r.location))
        session.commit()
    finally:
        session.close()

    return result
