from typing import List

from fastapi import APIRouter, Depends
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from ...db import Campus, Place
from ..utils import get_db

campus_router = APIRouter()


@campus_router.get("/", response_model=List[Campus])
async def get_campuses(db: Session = Depends(get_db)):
    return db.exec(select(Campus)).all()


@campus_router.get("/{campus_id}/places/", response_model=Page[Place])
async def get_campus_places(campus_id: int, db: Session = Depends(get_db)):
    return paginate(
        db,
        select(Place).join(Campus).where(Campus.id == campus_id),
    )


add_pagination(campus_router)
