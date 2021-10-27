from sqlmodel import Field, SQLModel, Relationship

# sqlalchemy debería ser evitado, pero la API de sqlmodel no es tan completa aún
from sqlalchemy.sql.sqltypes import Enum as SQLEnum
from sqlalchemy import Column

# NOTE(benjavicente): para las ubicaciones se podria usar postgis,
#                     pero no hay un buen ORM para añadirlo a este esquema

# from geoalchemy2 import Geometry


from typing import Optional, List
import enum
from datetime import datetime, date


# JoinTables tienen que estar antes de los modelos que unen


class SubjectEquivalencies(SQLModel, table=True):
    # __tablename__ = "subject_equivalencies"  # type: ignore
    subject_id: Optional[int] = Field(default=None, foreign_key="subject.id", primary_key=True)
    equivalence_id: Optional[int] = Field(default=None, foreign_key="subject.id", primary_key=True)


class CoursesTeachers(SQLModel, table=True):
    course_id: Optional[int] = Field(default=None, foreign_key="course.id", primary_key=True)
    teacher_id: Optional[int] = Field(default=None, foreign_key="teacher.id", primary_key=True)


RequirementRelationEnum = enum.Enum("RequirementRelationEnum", ["and", "or", "null"])


class Subject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    credits: Optional[int] = None
    code: str
    courses: List["Course"] = Relationship(back_populates="subject")
    school_id: Optional[int] = Field(default=None, foreign_key="school.id")
    school: Optional["School"] = Relationship(back_populates="subjects")
    syllabus: Optional[str] = None
    academic_level: Optional[str] = None
    description: Optional[str] = None
    restrictions: Optional[str] = None
    prerequisites_raw: Optional[str] = None
    requirements_relation: Optional[RequirementRelationEnum] = Field(
        default=None,
        sa_column=Column(SQLEnum(RequirementRelationEnum)),
    )
    prerequisites: List["PrerequisitesOrGroupElement"] = Relationship(
        back_populates="subjects",
    )

    # TODO
    # equivalences: List["Subject"] = Relationship(
    #     back_populates="equivalences",
    #     link_model=SubjectEquivalencies,
    # )

    def __repr__(self) -> str:
        return f"<{type(self).__name__} code={repr(self.code)}>"

    # NOTE(benjavicente): pydantic no soporta getters y setters
    def get_prerequisites(self) -> List[List["Subject"]]:
        return [[g.subject for g in g_or.child_and_groups] for g_or in self.prerequisites]

    def set_prerequisites(self, value: List[List["Subject"]]):
        group: List["PrerequisitesOrGroupElement"] = []
        for and_group in value:
            or_group_container = PrerequisitesOrGroupElement()
            for subject in and_group:
                subject_relation = PrerequisitesAndGroupElement(subject=subject)
                or_group_container.child_and_groups.append(subject_relation)
            group.append(or_group_container)
        self.prerequisites = group


class PrerequisitesOrGroupElement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: Optional[int] = Field(default=None, foreign_key="subject.id")
    subject: Subject = Relationship(back_populates="prerequisites")
    child_and_groups: List["PrerequisitesAndGroupElement"] = Relationship(
        sa_relationship_kwargs=dict(lazy="joined")
    )
    subjects: List["Subject"] = Relationship()

    def __repr__(self) -> str:
        return f"<{type(self).__name__} [{[g.subject for g in self.child_and_groups]}]>"


class PrerequisitesAndGroupElement(SQLModel, table=True):
    prerequisites_or_group_element_id: Optional[int] = Field(
        default=None,
        foreign_key="PrerequisitesOrGroupElement.id".lower(),
        primary_key=True,
    )
    prerequisites_or_group_element: PrerequisitesOrGroupElement = Relationship()
    subject_id: Optional[int] = Field(
        default=None,
        foreign_key="subject.id",
        primary_key=True,
    )
    subject: "Subject" = Relationship()


class RestrictionsOrGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subject.id")


class RestrictionsAndGroup(SQLModel, table=True):
    restrictions_or_group_id: int = Field(foreign_key="restrictionsorgroup.id", primary_key=True)
    restriction: str


PeriodEnum = enum.Enum("PeriodEnum", ["S1", "S2", "TAV"])

class Term(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    period: PeriodEnum = Field(sa_column=Column(SQLEnum(PeriodEnum)))
    first_class_day: Optional[date] = None
    last_class_day: Optional[date] = None
    last_day: Optional[date] = None

class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: Optional[int] = Field(default=None, foreign_key="subject.id")
    subject: Subject = Relationship(back_populates="courses")
    term_id: Optional[int] = Field(default=None, foreign_key="term.id")
    term: Term = Relationship()
    section: int
    nrc: str
    schedule_summary: str
    campus_id: Optional[int] = Field(default=None, foreign_key="campus.id")
    campus: "Campus" = Relationship()
    faculty_id: Optional[int] = Field(default=None, foreign_key="faculty.id")
    faculty: "Faculty" = Relationship()
    format: Optional[str]
    category: Optional[str]
    fg_area: Optional[str]
    is_removable: Optional[bool]
    is_english: Optional[bool]
    need_special_aproval: Optional[bool]
    available_quota: Optional[int]
    total_quota: Optional[int]
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
    classroom: Optional[str] = None
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
    website: Optional[str] = None
    description: Optional[str] = None
    campus_id: Optional[int] = Field(default=None, foreign_key="campus.id")
    campus: Campus = Relationship(back_populates="faculties")


class CategoryOfPlace(SQLModel, table=True):
    category_id: Optional[int] = Field(
        default=None, foreign_key="placecategory.id", primary_key=True
    )
    place_id: Optional[int] = Field(default=None, foreign_key="place.id", primary_key=True)


class Place(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lat: float
    lng: float
    # latLng: list = Field(sa_column=Column(Geometry("POINT")))
    # polygon: Optional[list] = Field(default=None, sa_column=Column(Geometry("POLYGON")))
    campus_id: Optional[int] = Field(default=None, foreign_key="campus.id")
    campus: Campus = Relationship(back_populates="places")
    name: str
    floor: Optional[int] = None
    notes: Optional[str] = None
    description: Optional[str] = None
    categories: List["PlaceCategory"] = Relationship(
        back_populates="places",
        link_model=CategoryOfPlace,
    )
    parent_id: Optional[int] = Field(default=None, foreign_key="place.id")
    parent: "Place" = Relationship(back_populates="child")
    child: "Place" = Relationship()


class PlaceCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    places: list[Place] = Relationship(back_populates="categories", link_model=CategoryOfPlace)


class UniversityEvents(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    start: datetime
    end: datetime
    tag: str
    description: Optional[str]
    is_a_holiday: bool = False
