from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from ...db import Course, Subject, Term
from ..models import CourseResponse, SubjectFullResponse, SubjectResponse
from ..utils import get_db

subject_router = APIRouter()


@subject_router.get("/", response_model=Page[SubjectResponse])
def get_subjects(db: Session = Depends(get_db)):
    return paginate(db, select(Subject))


@subject_router.get("/{subject_code}/", response_model=SubjectFullResponse)
def get_subject(subject_code: str, db: Session = Depends(get_db)):
    s = db.exec(select(Subject).where(Subject.code == subject_code)).one_or_none()
    if s is None:
        raise HTTPException(404)
    return s


@subject_router.get("/{subject_code}/sections/", response_model=Page[CourseResponse])
def get_subject_sections(
    subject_code: str, year: int = None, period: str = None, db: Session = Depends(get_db)
):
    query = select(Course).join(Subject).where(Subject.code == subject_code)
    if year is not None:
        query = query.join(Term).where(Term.year == year)

        if period is not None:
            query = query.where(Term.period == period)

    return paginate(db, query)


add_pagination(subject_router)
