from fastapi import APIRouter, Depends
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from ...db import School, Subject
from ..utils import get_db

school_router = APIRouter()


@school_router.get("/", response_model=Page[School])
def get_schools(db: Session = Depends(get_db)):
    return paginate(db, select(School))


@school_router.get("/{school_id}/subjects/", response_model=Page[Subject])
async def get_school_subjects(school_id: int, db: Session = Depends(get_db)):
    return paginate(
        db,
        select(Subject).join(School).where(School.id == Subject.school_id, School.id == school_id),
    )


add_pagination(school_router)
