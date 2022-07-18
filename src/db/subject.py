import enum
from typing import List, Optional

from sqlalchemy import Column

# sqlalchemy debería ser evitado, pero la API de sqlmodel no es tan completa aún
from sqlalchemy.sql.sqltypes import Enum as SQLEnum
from sqlmodel import Field, Relationship, SQLModel

from .places import Campus
from .term import Term

# JoinTables tienen que estar antes de los modelos que unen


class SubjectEquivalencies(SQLModel, table=True):  # type: ignore  # noqa
    """Join model for equivalent subjects.
    All of the equivalencies of at least one group should be met to satisfy the equivalency"""

    subject_id: int = Field(default=None, foreign_key="subject.id", primary_key=True)
    equivalence_id: int = Field(default=None, foreign_key="subject.id", primary_key=True)
    group: int = Field(default=None, primary_key=True)

    equivalence: "Subject" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[SubjectEquivalencies.equivalence_id]"}
    )


class SubjectPrerequisites(SQLModel, table=True):  # type: ignore  # noqa
    """Join model for subject prerequisites, organized by groups.
    All of the prerequsites of at least one group should be met to satisfy the requirements"""

    subject_id: int = Field(default=None, foreign_key="subject.id", primary_key=True)
    prerequisite_id: int = Field(default=None, foreign_key="subject.id", primary_key=True)
    group: int = Field(default=None, primary_key=True)
    is_corequisite: bool

    prerequisite: "Subject" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[SubjectPrerequisites.prerequisite_id]"}
    )


class CoursesTeachers(SQLModel, table=True):  # type: ignore  # noqa
    """Join model for courses teachers"""

    course_id: int = Field(default=None, foreign_key="course.id", primary_key=True)
    teacher_id: int = Field(default=None, foreign_key="teacher.id", primary_key=True)


class Subject(SQLModel, table=True):  # type: ignore  # noqa
    """Subject from Catalogo UC"""

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
    equivalencies_raw: Optional[str] = None
    need_all_requirements: bool = False  # Requirements relation
    is_active: Optional[bool] = None

    prerequisites: List[SubjectPrerequisites] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[SubjectPrerequisites.subject_id]"},
    )

    unlocks: List["Subject"] = Relationship(
        link_model=SubjectPrerequisites,
        sa_relationship_kwargs={
            "primaryjoin": "Subject.id==SubjectPrerequisites.prerequisite_id",
            "secondaryjoin": "Subject.id==SubjectPrerequisites.subject_id",
        },
    )

    equivalencies: List[SubjectEquivalencies] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[SubjectEquivalencies.subject_id]"},
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


class Course(SQLModel, table=True):  # type: ignore  # noqa
    """Instance of a Subject dictated in a Term and specific section.
    Represents a course from Buscacursos."""

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
    """Monday to Saturday days"""

    L = "L"
    M = "M"
    W = "W"
    J = "J"
    V = "V"
    S = "S"


class ClassSchedule(SQLModel, table=True):  # type: ignore  # noqa
    """Module of a course in a week"""

    id: Optional[int] = Field(default=None, primary_key=True)
    day: DayEnum = Field(sa_column=Column(SQLEnum(DayEnum)))
    module: int = Field(ge=1, le=8)  # [1, 2, 3, 4, 5, 6, 7, 8]
    classroom: Optional[str] = None
    type: Optional[str] = None
    course_id: Optional[int] = Field(default=None, foreign_key="course.id")
    course: Course = Relationship(back_populates="schedule")


class Teacher(SQLModel, table=True):  # type: ignore  # noqa
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    photo_url: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    courses: List["Course"] = Relationship(back_populates="teachers", link_model=CoursesTeachers)


class School(SQLModel, table=True):  # type: ignore  # noqa
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    website: Optional[str] = None
    description: Optional[str] = None
    subjects: List[Subject] = Relationship(back_populates="school")
