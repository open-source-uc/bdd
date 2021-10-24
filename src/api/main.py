from fastapi import FastAPI
from .graphql import graphql_app

from sqlmodel import Session, select
from ..db import Campus, create_dbb, engine


app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

@app.on_event("startup")
def on_startup():
    create_dbb()


@app.get("/campuses")
async def campuses():
    with Session(engine) as session:
        return session.exec(select(Campus)).all()
