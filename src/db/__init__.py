import os
from sqlmodel import create_engine as _create_engine, SQLModel

from .schema import (
    Campus,
    CategoryOfPlace,
    ClassSchedule,
    Course,
    CoursesTeachers,
    Faculty,
    Place,
    PlaceCategory,
    PrerequisitesAndGroupElement,
    PrerequisitesOrGroupElement,
    RestrictionsAndGroup,
    RestrictionsOrGroup,
    School,
    Subject,
    SubjectEquivalencies,
    Teacher,
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
    SQLModel.metadata.create_all(engine)
