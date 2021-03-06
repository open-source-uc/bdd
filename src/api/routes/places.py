from fastapi import APIRouter, Depends
from fastapi_pagination import Page, add_pagination, paginate
from sqlmodel import Session, select

from ...db import Place
from ..utils import get_db

place_router = APIRouter()


@place_router.get("/", response_model=Page[Place])
async def get_places(db: Session = Depends(get_db)):
    return paginate(db, select(Place))


add_pagination(place_router)
