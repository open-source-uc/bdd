from fastapi import APIRouter, Depends
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from ...db import Course
from ..utils import get_db

course_router = APIRouter()


@course_router.get("/", response_model=Page[Course])
def get_courses(db: Session = Depends(get_db)):
    return paginate(db, select(Course))


add_pagination(course_router)
