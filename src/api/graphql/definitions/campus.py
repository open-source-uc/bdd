from typing import List

import strawberry
from sqlmodel import Session, select

from ....db import Campus, engine


@strawberry.experimental.pydantic.type(model=Campus, all_fields=True, name="Campus")
class GraphQLCampus:
    pass


@strawberry.type
class CampusQuery:
    @strawberry.field()
    def all_campuses(self) -> List[GraphQLCampus]:
        with Session(engine) as session:
            return session.exec(select(Campus)).all()  # type: ignore
