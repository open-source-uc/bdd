from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ...db import Term
from ..utils import get_db

terms_router = APIRouter()

@terms_router.get("/", response_model=list[Term])
def get_subjects(db: Session = Depends(get_db)):
    return db.exec(select(Term)).all()
