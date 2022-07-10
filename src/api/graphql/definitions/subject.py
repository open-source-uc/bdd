from typing import List

import strawberry
from sqlmodel import Session, select

from ....db import Subject, engine

# TODO: add pagination


@strawberry.experimental.pydantic.type(model=Subject, fields=["id", "name", "initials"])
class GQLSubject:
    pass


@strawberry.type
class SubjectQuery:
    @strawberry.field()
    def all_subjects(self) -> List[GQLSubject]:
        with Session(engine) as session:
            return session.exec(select(Subject)).all()  # type: ignore
