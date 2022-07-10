from fastapi import APIRouter, Depends
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from ...db import Teacher
from ..utils import get_db

teacher_router = APIRouter()


@teacher_router.get("/", response_model=Page[Teacher])
def get_teachers(db: Session = Depends(get_db)):
    return paginate(db, select(Teacher))


add_pagination(teacher_router)
