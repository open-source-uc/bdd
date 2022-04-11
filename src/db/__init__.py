from sqlmodel import create_engine as _create_engine, SQLModel
from ..config import config

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


def create_engine(*, user: str, password: str, db_name: str, host: str, driver: str = "postgresql"):
    return _create_engine(f"{driver}://{user}:{password}@{host}/{db_name}", )


engine = create_engine(
    user=config.db_user,
    password=config.db_password,
    host=config.db_host,
    db_name=config.db_name,
)


def create_db(clean: bool = False):
    if clean:
        SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
