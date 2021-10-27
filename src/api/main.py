from fastapi import FastAPI
from fastapi_pagination import add_pagination

from ..db import create_db

from .graphql import graphql_app
from .routes.campus import campus_router
from .routes.subject import subject_router

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
app.include_router(campus_router, prefix="/campus")
app.include_router(subject_router, prefix="/subject")

@app.on_event("startup")
def on_startup():
    create_db()
