import os

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://{user}:{pw}@{host}:{port}/{db}".format(
        user=os.getenv("POSTGRES_USER", "postgres"),
        pw=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "db"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        db=os.getenv("POSTGRES_DB", "postgres"),
    ),
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Record(Base):
    __tablename__ = "records"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    name     = Column(String,  nullable=False)
    age      = Column(Integer, nullable=False)
    email    = Column(String,  nullable=False)
    location = Column(String,  nullable=False)
