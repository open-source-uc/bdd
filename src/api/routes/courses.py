from typing import Union
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, col

from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate

from src.db.schema import Term

from ...db import Course, Subject
from ..utils import get_db

course_router = APIRouter()


@course_router.get("/", response_model=Page[Course])
def get_courses(
    db: Session = Depends(get_db),
    q: Union[str, None] = None,
    term_id: Union[int, None] = None,
    credits: Union[int, None] = None,
    campus_ids: Union[list[int], None] = None,
    school_ids: Union[list[int], None] = None,
    fg_areas: Union[list[str], None] = None,
    categories: Union[list[str], None] = None,
    formats: Union[list[str], None] = None,
    without_req: Union[bool, None] = None,
    with_quota: Union[bool, None] = None,
    schedule: Union[list[str], None] = None,
    allow_schedule_collisions: Union[bool, None] = None,
):
    query = select(Course).join(Subject).where(Course.subject_id == Subject.id)
    # Filter query (numeric, initials, name or teacher)
    if q is not None:
        pass

    if term_id is not None:
        query = query.join(Term).where(Course.term_id == Term.id, Term.id == term_id)

    if credits is not None:
        query = query.where(Subject.credits == credits)

    if campus_ids is not None:
        query = query.where(col(Course.campus_id).in_(campus_ids))

    if school_ids is not None:
        query = query.where(col(Subject.school_id).in_(school_ids))

    if fg_areas is not None:
        query = query.where(col(Course.fg_area).in_(fg_areas))

    if categories is not None:
        query = query.where(col(Course.category).in_(categories))

    if formats is not None:
        query = query.where(col(Course.format).in_(formats))
    # Filter with requirements
    if without_req is True:
        pass
    # Filter schedule
    if schedule is not None:
        if allow_schedule_collisions is True:
            pass
    # Filter no quota
    if with_quota is True:
        pass

    return paginate(db, query)


@course_router.get("/{id}")
def get_course(id: int, db: Session = Depends(get_db)) -> Course:
    course = db.exec(select(Course).where(Course.id == id)).one_or_none()
    if course is None:
        raise HTTPException(404)

    # TODO: include schedule, related, etc
    return course


@course_router.get("/{id}/banner")
def get_course_banner(id: int, db: Session = Depends(get_db)) -> list:
    course = db.exec(select(Course).where(Course.id == id)).one_or_none()
    if course is None:
        raise HTTPException(404)

    # TODO: return banner info (quotas)
    return []


add_pagination(course_router)
