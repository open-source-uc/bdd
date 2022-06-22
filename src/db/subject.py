import enum
from typing import List, Optional

from sqlalchemy import Column
from .term import Term
from .places import Campus

# sqlalchemy debería ser evitado, pero la API de sqlmodel no es tan completa aún
from sqlalchemy.sql.sqltypes import Enum as SQLEnum
from sqlmodel import Field, Relationship, SQLModel


# JoinTables tienen que estar antes de los modelos que unen


class SubjectEquivalencies(SQLModel, table=True):
    subject_id: int = Field(default=None, foreign_key="subject.id", primary_key=True)
    equivalence_id: int = Field(default=None, foreign_key="subject.id", primary_key=True)


class SubjectPrerequisites(SQLModel, table=True):
    subject_id: int = Field(default=None, foreign_key="subject.id", primary_key=True)
    prerequisite_id: int = Field(default=None, foreign_key="subject.id", primary_key=True)


class CoursesTeachers(SQLModel, table=True):
    course_id: int = Field(default=None, foreign_key="course.id", primary_key=True)
    teacher_id: int = Field(default=None, foreign_key="teacher.id", primary_key=True)


class Subject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    credits: int
    code: str
    courses: List["Course"] = Relationship(back_populates="subject")
    school_id: Optional[int] = Field(default=None, foreign_key="school.id")
    school: Optional["School"] = Relationship(back_populates="subjects")
    syllabus: Optional[str] = Field(None, index=False)
    academic_level: Optional[str] = None
    description: Optional[str] = None
    restrictions: Optional[str] = None
    prerequisites_raw: Optional[str] = None
    need_all_requirements: bool = False  # Requirements relation

    prerequisites: List["Subject"] = Relationship(
        back_populates="unlocks",
        link_model=SubjectPrerequisites,
        sa_relationship_kwargs={
            "primaryjoin": "Subject.id==SubjectPrerequisites.subject_id",
            "secondaryjoin": "Subject.id==SubjectPrerequisites.prerequisite_id",
        },
    )
    unlocks: List["Subject"] = Relationship(
        back_populates="prerequisites",
        link_model=SubjectPrerequisites,
        sa_relationship_kwargs={
            "primaryjoin": "Subject.id==SubjectPrerequisites.prerequisite_id",
            "secondaryjoin": "Subject.id==SubjectPrerequisites.subject_id",
        },
    )

    equivalences: List["Subject"] = Relationship(
        link_model=SubjectEquivalencies,
        sa_relationship_kwargs={
            "primaryjoin": "Subject.id==SubjectEquivalencies.subject_id",
            "secondaryjoin": "Subject.id==SubjectEquivalencies.equivalence_id",
        },
    )

    # __table_args__ = (
    #     Index(
    #         "subject_syllabus_full_text_search_index",
    #         sql.func.to_tsvector("english", syllabus),
    #         postgresql_using="gin",
    #     ),
    # )

    def __repr__(self) -> str:
        return f"<{type(self).__name__} code={repr(self.code)}>"


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: Optional[int] = Field(default=None, foreign_key="subject.id")
    subject: Subject = Relationship(back_populates="courses")
    term_id: Optional[int] = Field(default=None, foreign_key="term.id")
    term: Term = Relationship()
    section: int
    nrc: str
    schedule_summary: Optional[str]
    campus_id: Optional[int] = Field(default=None, foreign_key="campus.id")
    campus: "Campus" = Relationship()
    format: Optional[str]
    category: Optional[str]
    fg_area: Optional[str]
    is_removable: Optional[bool]
    is_english: Optional[bool]
    need_special_aproval: Optional[bool]
    schedule: List["ClassSchedule"] = Relationship(back_populates="course")
    available_quota: Optional[int]
    total_quota: Optional[int]
    teachers: List["Teacher"] = Relationship(back_populates="courses", link_model=CoursesTeachers)


class DayEnum(str, enum.Enum):
    L = "L"
    M = "M"
    W = "W"
    J = "J"
    V = "V"
    S = "S"


class ClassSchedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    day: DayEnum = Field(sa_column=Column(SQLEnum(DayEnum)))
    module: int = Field(ge=1, le=8)  # [1, 2, 3, 4, 5, 6, 7, 8]
    classroom: Optional[str] = None
    type: Optional[str] = None
    course_id: Optional[int] = Field(default=None, foreign_key="course.id")
    course: Course = Relationship(back_populates="schedule")


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