import os
from sqlmodel import create_engine as _create_engine, SQLModel

from .schema import (
    Campus,
    Course,
    Faculty,
    Place,
    School,
    Subject,
    Teacher,
    UniversityEvents,
)

def create_engine(*, user, password, db_name, driver = "postgresql"):
    return _create_engine(f"{driver}://{user}:{password}@localhost/{db_name}")

engine = create_engine(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASWORD"),
    db_name=os.getenv("DB_NAME"),
)

def create_db():
    SQLModel.metadata.create_all(engine)
