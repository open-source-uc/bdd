from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class UniversityEvents(SQLModel, table=True):  # type: ignore  # noqa
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    start: datetime
    end: datetime
    tag: str
    description: Optional[str]
    is_a_holiday: bool = False
