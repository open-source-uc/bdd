from typing import List

from fastapi import APIRouter, Depends
from fastapi_pagination import add_pagination
from sqlmodel import Session, select

from ...db import Place
from ..utils import get_db

place_router = APIRouter()


@place_router.get("/", response_model=List[Place])
async def get_places(db: Session = Depends(get_db)):
    return db.exec(select(Place)).all()


add_pagination(place_router)
