import enum
from datetime import date
from typing import Optional

from sqlalchemy import Column

# sqlalchemy debería ser evitado, pero la API de sqlmodel no es tan completa aún
from sqlalchemy.sql.sqltypes import Enum as SQLEnum
from sqlmodel import Field, SQLModel


class PeriodEnum(str, enum.Enum):
    s1 = "S1"
    s2 = "S2"
    tav = "TAV"

    # NOTA(benjavicente): No se como se puede hacer esto más simple

    def __int__(self):
        # Convierte las siglas a numeros al hacer int(periodo)
        return ["S1", "S2", "TAV"].index(self.value) + 1

    @classmethod
    def from_int(cls, value: int):
        return cls(["S1", "S2", "TAV"][value - 1])


class Term(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    period: PeriodEnum = Field(sa_column=Column(SQLEnum(PeriodEnum)))
    first_class_day: Optional[date] = None
    last_class_day: Optional[date] = None
    last_day: Optional[date] = None
