import os

from sqlmodel import SQLModel
from sqlmodel import create_engine as _create_engine

from .schema import (
    Campus,
    CategoryOfPlace,
    ClassSchedule,
    Course,
    CoursesTeachers,
    DayEnum,
    PeriodEnum,
    Place,
    PlaceCategory,
    PrerequisitesAndGroupElement,
    PrerequisitesOrGroupElement,
    RequirementRelationEnum,
    RestrictionsAndGroup,
    RestrictionsOrGroup,
    School,
    Subject,
    SubjectEquivalencies,
    Teacher,
    Term,
    UniversityEvents,
)


def create_engine(*, user: str, password: str, db_name: str, driver: str = "postgresql"):
    return _create_engine(f"{driver}://{user}:{password}@localhost/{db_name}")


engine = create_engine(
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASWORD"],
    db_name=os.environ["DB_NAME"],
)


def create_db():
    # Se puede descomentar lo siguiente para partir la BDD de 0
    # SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
