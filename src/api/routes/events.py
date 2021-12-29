from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate

from ...db import UniversityEvents
from ..utils import get_db

event_router = APIRouter()


@event_router.get("/", response_model=Page[UniversityEvents])
def get_events(db: Session = Depends(get_db)):
    return paginate(db, select(UniversityEvents))


add_pagination(event_router)
