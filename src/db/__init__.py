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

from sqlmodel import create_engine as _create_engine, SQLModel

engine = _create_engine("postgresql://benjavicente:benjavicente@localhost/bdduc")


def create_db():
    SQLModel.metadata.create_all(engine)
