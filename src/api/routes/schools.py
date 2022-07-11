from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from ...db import School, Subject
from ..utils import get_db

school_router = APIRouter()


@school_router.get("/", response_model=Page[School])
def get_schools(db: Session = Depends(get_db)):
    return paginate(db, select(School))

@school_router.get("/{id}/")
def get_school(id: int, db: Session = Depends(get_db)) -> School:
    school = db.exec(select(School).where(School.id == id)).one_or_none()
    if school is None:
        raise HTTPException(404)

    return school


@school_router.get("/{school_id}/subjects/", response_model=Page[Subject])
async def get_school_subjects(school_id: int, db: Session = Depends(get_db)):
    return paginate(db, select(Subject).where(School.id == school_id))


add_pagination(school_router)
