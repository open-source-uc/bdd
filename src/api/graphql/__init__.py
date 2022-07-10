# Full example: https://github.com/aryaniyaps/examples/tree/main/reddit-clone

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.tools import merge_types

from .definitions.campus import CampusQuery
from .definitions.subject import SubjectQuery

schema = strawberry.Schema(
    query=merge_types(
        name="query",
        types=(
            CampusQuery,
            SubjectQuery,
        ),
    )
)

graphql_app = GraphQLRouter(schema)
