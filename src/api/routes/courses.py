import re
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, col, select

from ...db import Course, Subject, Term
from ..utils import get_db

course_router = APIRouter()

NUMBERS_EXP = re.compile(r"^\d{1,4}$")
SUBJECT_CODE_EXP = re.compile(r"^[a-zA-Z]{1,3}(\d{3,4}[a-zA-Z]?|\d{0,4})$")


@course_router.get("/", response_model=Page[Course])
def get_courses(
    db: Session = Depends(get_db),
    q: Union[str, None] = Query(
        None, description="Query term: NRC, partial subject code or name, teacher name"
    ),
    term_id: Union[int, None] = None,
    credits: Union[int, None] = None,
    campus_ids: list[int] = Query([]),
    school_ids: list[int] = Query([]),
    fg_areas: list[str] = Query([]),
    categories: list[str] = Query([]),
    formats: list[str] = Query([]),
    without_req: bool = Query(False, description="Discard courses with prerequisites"),
    with_quota: bool = Query(False, description="Discard courses without available quota"),
    blocked_schedule: list[str] = Query(
        [], description="Discard courses colliding with this modules"
    ),
    allow_ayu_and_lab_collisions: bool = Query(
        False, description="Ignore schedule collisions with AYU and LAB modules"
    ),
):
    query = select(Course).join(Subject).where(Course.subject_id == Subject.id)
    if q is not None:
        if NUMBERS_EXP.match(query):
            query = query.where(Course.nrc == q)

        elif SUBJECT_CODE_EXP.match(query):
            query = query.where(col(Subject.code).startswith(q.upper()))

        else:
            query = query.where(
                col(Subject.name).contains(q)
            )  # TODO: match teachers (or), case-insensitive, unaccent

    if term_id is not None:
        query = query.join(Term).where(Course.term_id == Term.id, Term.id == term_id)

    if credits is not None:
        query = query.where(Subject.credits == credits)

    if len(campus_ids) != 0:
        query = query.where(col(Course.campus_id).in_(campus_ids))

    if len(school_ids) != 0:
        query = query.where(col(Subject.school_id).in_(school_ids))

    if len(fg_areas) != 0:
        query = query.where(col(Course.fg_area).in_(fg_areas))

    if len(categories) != 0:
        query = query.where(col(Course.category).in_(categories))

    if len(formats) != 0:
        query = query.where(col(Course.format).in_(formats))

    if without_req:
        query = query.where(Subject.prerequisites_raw != "No tiene")

    if with_quota:
        query = query.where(Course.available_quota != 0)

    if len(blocked_schedule) != 0:
        # TODO: filter by schedule
        if allow_ayu_and_lab_collisions:
            pass

    return paginate(db, query)


@course_router.get("/{id}/")
def get_course(id: int, db: Session = Depends(get_db)) -> Course:
    course = db.exec(select(Course).where(Course.id == id)).one_or_none()
    if course is None:
        raise HTTPException(404)

    # TODO: include schedule, related, etc
    return course


@course_router.get("/{id}/banner/")
def get_course_banner(id: int, db: Session = Depends(get_db)) -> list:
    course = db.exec(select(Course).where(Course.id == id)).one_or_none()
    if course is None:
        raise HTTPException(404)

    # TODO: return banner info (quotas)
    return []


add_pagination(course_router)
