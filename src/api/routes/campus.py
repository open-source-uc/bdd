from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ...db import Campus
from ..utils import get_db

campus_router = APIRouter()

@campus_router.get("/")
async def get_campuses(db: Session = Depends(get_db)):
    return db.exec(select(Campus)).all()
