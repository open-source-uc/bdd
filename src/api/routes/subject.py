from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from ...db import Course, PeriodEnum, Subject, Term
from ..utils import get_db

subject_router = APIRouter()


@subject_router.get("/", response_model=Page[Subject])
def get_subjects(db: Session = Depends(get_db)):
    return paginate(db, select(Subject))


@subject_router.get("/{subject_code}", response_model=Subject)
def get_subject(subject_code: str, db: Session = Depends(get_db)):
    s = db.exec(select(Subject).where(Subject.code == subject_code)).one_or_none()
    if s is None:
        raise HTTPException(404)

    # TODO: Subject should include requirements and school
    return s


@subject_router.get("/{subject_code}/sections", response_model=Page[Course])
def get_subject_sections(
    subject_code: str, year: int = None, period: str = None, db: Session = Depends(get_db)
):
    query = (
        select(Course)
        .join(Subject)
        .where(Course.subject_id == Subject.id, Subject.code == subject_code)
    )
    if year is not None:
        query = query.join(Term).where(Term.id == Course.term_id, Term.year == year)

        if period is not None:
            query = query.where(Term.period == period)

    return paginate(db, query)


@subject_router.get("/{id}/requirements/", response_model=list[list[Subject]])
def get_subject_requirements(id: int, db: Session = Depends(get_db)):
    s = db.exec(select(Subject).where(Subject.id == id)).one_or_none()
    if s is None:
        raise HTTPException(404)

    return s.get_prerequisites()


@subject_router.get("/{id}/sections")
def get_all_course_sections(id: int, db: Session = Depends(get_db)) -> List[Course]:
    subject = db.exec(select(Subject).where(Subject.id == id)).one_or_none()
    if subject is None:
        raise HTTPException(404)

    return db.exec(select(Course).where(Course.subject_id == id)).all()


@subject_router.get("/{id}/{year}/{period}/")
def get_all_course_sections_by_academic_period(
    id: int,
    year: int,
    period: PeriodEnum,
    db: Session = Depends(get_db),
):
    subject = db.exec(select(Subject).where(Subject.id == id)).one_or_none()
    if subject is None:
        raise HTTPException(404)

    # TODO: inlcude: { model: Course, where: course.randido_en = periodo academico }
    return db.exec(
        select(Course, Subject, Term).where(
            Course.subject_id == id,
            Term.year == year,
            Term.period == period,
            Course.subject_id == Subject.id,
            Term.id == Course.term_id,
        )
    ).all()


add_pagination(subject_router)
