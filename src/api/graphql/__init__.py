# Full example: https://github.com/aryaniyaps/examples/tree/main/reddit-clone

# Move this to another file
import strawberry
from typing import List
from sqlmodel import Session, select
from ...db import Campus, engine


@strawberry.experimental.pydantic.type(model=Campus, all_fields=True)
class GraphQLCampus:
    pass


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"

    @strawberry.field
    def campuses(self) -> List[GraphQLCampus]:
        with Session(engine) as session:
            return session.exec(select(Campus)).all()  # type: ignore


# __init__.py
from strawberry.fastapi import GraphQLRouter

schema = strawberry.Schema(Query)
graphql_app = GraphQLRouter(schema)
