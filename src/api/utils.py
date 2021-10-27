from typing import Iterator
from sqlmodel import Session

from ..db import engine


def get_db() -> Iterator[Session]:
    db = Session(engine)
    try:
        yield db
    finally:
        db.commit()
        db.close()
