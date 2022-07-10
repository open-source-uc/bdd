from fastapi import APIRouter, Depends
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from ...db import Faculty
from ..utils import get_db

faculty_router = APIRouter()


@faculty_router.get("/", response_model=Page[Faculty])
def get_faculties(db: Session = Depends(get_db)):
    return paginate(db, select(Faculty))


add_pagination(faculty_router)
