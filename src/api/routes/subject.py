from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate

from ...db import Subject
from ..utils import get_db

subject_router = APIRouter()

@subject_router.get("/", response_model=Page[Subject])
def get_subjects(db: Session = Depends(get_db)):
    return paginate(db, select(Subject))

add_pagination(subject_router)
