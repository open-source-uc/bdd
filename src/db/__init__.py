from .schema import Campus

from sqlmodel import create_engine as _create_engine, SQLModel

engine = _create_engine("postgresql://benjavicente:benjavicente@localhost/bdduc")


def create_dbb():
    SQLModel.metadata.create_all(engine)
