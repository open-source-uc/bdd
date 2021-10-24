from sqlalchemy.orm import relation
from sqlmodel import Field, SQLModel, Relationship, Session

# sqlalchemy debería ser evitado, pero la API de sqlmodel no es tan completa aún
from sqlalchemy.sql.sqltypes import Enum
from sqlalchemy import Column
# from geoalchemy2 import Geometry


from typing import Optional, List
import enum
from datetime import datetime


# JoinTables tienen que estar antes de los modelos que unen


class SubjectEquivalencies(SQLModel, table=True):
    # __tablename__ = "subject_equivalencies"  # type: ignore
    subject_id: int = Field(foreign_key="subject.id", primary_key=True)
    equivalence_id: int = Field(foreign_key="subject.id", primary_key=True)


class CoursesTeachers(SQLModel, table=True):
    course_id: Optional[int] = Field(default=None, foreign_key="course.id", primary_key=True)
    teacher_id: Optional[int] = Field(default=None, foreign_key="teacher.id", primary_key=True)


RequirementRelationEnum = enum.Enum("RequirementRelationEnum", ["and", "or", "null"])


class Subject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    credits: int
    initials: str
    courses: List["Course"] = Relationship(back_populates="subject")
    school_id: Optional[int] = Field(default=None, foreign_key="school.id")
    school: Optional["School"] = Relationship(back_populates="subjects")
    syllabus: str
    academic_level: str
    description: str
    restrictions: str
    prerequisites_raw: str
    requirements_relation: RequirementRelationEnum = Field(
        sa_column=Column(Enum(RequirementRelationEnum))
    )
    # _prerequisites: list["PrerequisitesOrGroup"] = Relationship(back_populates="subjects")
    # equivalences: List["Subject"] = Relationship(
    #     back_populates="equivalences", link_model=SubjectEquivalencies,
    # )

    # @property
    # def prerequisites(self):
    #     return [[C1 & C2] | [C1 & C3]]


class PrerequisitesOrGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subject.id", primary_key=True)
    # subject: Subject = Relationship(back_populates="_prerequisites")


class PrerequisitesAndGroup(SQLModel, table=True):
    prerequisites_or_group_id: int = Field(foreign_key="restrictionsorgroup.id", primary_key=True)
    course_id: int = Field(foreign_key="course.id", primary_key=True)
    course: "Course" = Relationship()


class RestrictionsOrGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subject.id")


class RestrictionsAndGroup(SQLModel, table=True):
    restrictions_or_group_id: int = Field(foreign_key="restrictionsorgroup.id", primary_key=True)
    restriction: str


PeriodEnum = enum.Enum("PeriodEnum", ["S1", "S2", "TAV"])


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subject.id")
    subject: Subject = Relationship(back_populates="courses")
    year: int
    period: PeriodEnum = Field(sa_column=Column(Enum(PeriodEnum)))
    section: int
    nrc: str
    schedule_summary: str
    campus_id: int = Field(foreign_key="campus.id")
    campus: "Campus" = Relationship()
    faculty_id: int = Field(foreign_key="faculty.id")
    faculty: "Faculty" = Relationship()
    format: str
    category: str
    fg_area: str
    is_removable: bool
    is_english: bool
    need_special_aproval: bool
    available_quota: int
    total_quota: int
    teachers: List["Teacher"] = Relationship(back_populates="courses", link_model=CoursesTeachers)


class Campus(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    faculties: List["Faculty"] = Relationship()
    places: List["Place"] = Relationship()


DayEnum = enum.Enum("DayEnum", ["L", "M", "W", "J", "V", "S"])


class ClassSchedule:
    day: DayEnum
    module: int = Field(gt=1, lt=7)  # [1, 2, 3, 4, 5, 6, 7, 8]
    classroom: str
    course_id: Optional[str] = Field(default=None, foreign_key="course.id")
    course: Course = Relationship()


class Teacher(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    photo_url: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    courses: List["Course"] = Relationship(back_populates="teachers", link_model=CoursesTeachers)


class School(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    website: Optional[str] = None
    description: Optional[str] = None
    subjects: List[Subject] = Relationship(back_populates="school")


class Faculty(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    website: str
    description: str
    campus_id: int = Field(default=None, foreign_key="campus.id")
    campus: Campus = Relationship(back_populates="faculties")


class CategoryOfPlace(SQLModel, table=True):
    category_id: Optional[int] = Field(default=None, foreign_key="placecategory.id", primary_key=True)
    place_id: Optional[int] = Field(default=None, foreign_key="place.id", primary_key=True)


class Place(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lat: float
    lng: float
    # latLng: list = Field(sa_column=Column(Geometry("POINT")))
    # polygon: Optional[list] = Field(default=None, sa_column=Column(Geometry("POLYGON")))
    campus_id: int = Field(default=None, foreign_key="campus.id")
    campus: Campus = Relationship(back_populates="places")
    name: str
    floor: Optional[int] = None
    notes: Optional[str] = None
    description: Optional[str] = None
    categories: List["PlaceCategory"] = Relationship(
        back_populates="places", link_model=CategoryOfPlace,
    )
    parent_id: Optional[int] = Field(default=None, foreign_key="place.id")
    parent: "Place" = Relationship(back_populates="child")
    child: "Place" = Relationship()


class PlaceCategory(SQLModel, table=True):
    name: str
    id: Optional[int] = Field(default=None, primary_key=True)
    places: list[Place] = Relationship(back_populates="categories", link_model=CategoryOfPlace)


class UniversityEvents(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    start: datetime
    end: datetime
    tag: str
    description: str
    is_a_holiday: bool = False


if __name__ == "__main__":
    from sqlmodel import create_engine, SQLModel
    # engine = create_engine("sqlite://", echo=True)  # in memory temp DB
    engine = create_engine("postgresql://benjavicente:benjavicente@localhost/bdduc", echo=True)
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    # session.add(Place(lat=1, lng=3, name="lugar x"))
    # session.commit()
