from fastapi import FastAPI

from ..config import config
from ..db import create_db
from .graphql import graphql_app
from .routes.campus import campus_router
from .routes.courses import course_router
from .routes.events import event_router
from .routes.places import place_router
from .routes.schools import school_router
from .routes.subject import subject_router
from .routes.teachers import teacher_router
from .routes.terms import terms_router

app = FastAPI(root_path=str(config.api_base_path))

app.include_router(graphql_app, prefix="/graphql", tags=["GraphQL"])

app.include_router(course_router, prefix="/courses", tags=["Courses"])
app.include_router(campus_router, prefix="/campuses", tags=["Campuses"])
app.include_router(event_router, prefix="/events", tags=["Events"])
app.include_router(place_router, prefix="/places", tags=["Places"])
app.include_router(school_router, prefix="/schools", tags=["Schools"])
app.include_router(subject_router, prefix="/subjects", tags=["Subjects"])
app.include_router(teacher_router, prefix="/teachers", tags=["Teachers"])
app.include_router(terms_router, prefix="/terms", tags=["Terms"])


@app.on_event("startup")
def on_startup():
    create_db()
