from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate

from ...db import School
from ..utils import get_db

school_router = APIRouter()


@school_router.get("/", response_model=Page[School])
def get_schools(db: Session = Depends(get_db)):
    return paginate(db, select(School))


add_pagination(school_router)
