from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from ..db import create_db

from .graphql import graphql_app

from .routes.campus import campus_router
from .routes.events import event_router
from .routes.faculties import faculty_router
from .routes.places import place_router
from .routes.schools import school_router
from .routes.subject import subject_router
from .routes.teachers import teacher_router
from .routes.terms import terms_router


app = FastAPI()

app.include_router(graphql_app, prefix="/graphql", tags=["GraphQL"])

app.include_router(campus_router, prefix="/campus", tags=["Campus"])
app.include_router(event_router, prefix="/events", tags=["Events"])
app.include_router(faculty_router, prefix="/faculties", tags=["Faculties"])
app.include_router(place_router, prefix="/places", tags=["Places"])
app.include_router(school_router, prefix="/schools", tags=["Schools"])
app.include_router(subject_router, prefix="/subject", tags=["Subjects"])
app.include_router(teacher_router, prefix="/teachers", tags=["Teachers"])
app.include_router(terms_router, prefix="/terms", tags=["Terms"])


@app.on_event("startup")
def on_startup():
    create_db()
