from typing import List, Optional

from sqlmodel import SQLModel

from ..db import Campus, ClassSchedule, Teacher


class TermMinimal(SQLModel):
    year: int
    period: str


class SchoolMinimal(SQLModel):
    id: int
    name: str


class SubjectMinimal(SQLModel):
    code: str
    name: str


class EquivalencyResponse(SQLModel):
    group: int
    equivalence: SubjectMinimal


class PrerequisteResponse(SQLModel):
    group: int
    is_corequisite: bool
    prerequisite: SubjectMinimal


class SubjectResponse(SQLModel):
    id: int
    code: str
    name: str
    credits: int
    school: SchoolMinimal
    description: Optional[str]
    restrictions: Optional[str]
    prerequisites: List[PrerequisteResponse]
    need_all_requirements: bool


class SubjectFullResponse(SubjectResponse):
    is_active: Optional[bool]
    academic_level: Optional[str]
    syllabus: Optional[str]
    equivalencies: List[EquivalencyResponse]
    unlocks: List[SubjectMinimal]


class CourseResponse(SQLModel):
    id: int
    subject: SubjectMinimal
    term: TermMinimal
    section: int
    nrc: str
    schedule_summary: Optional[str]
    campus: Campus
    available_quota: Optional[int]
    total_quota: Optional[int]
    teachers: List[Teacher]


class CourseFullResponse(SQLModel):
    id: int
    subject: SubjectResponse
    term: TermMinimal
    section: int
    nrc: str
    schedule_summary: Optional[str]
    campus: Campus
    format: Optional[str]
    category: Optional[str]
    fg_area: Optional[str]
    is_removable: Optional[bool]
    is_english: Optional[bool]
    need_special_aproval: Optional[bool]
    schedule: List[ClassSchedule]
    available_quota: Optional[int]
    total_quota: Optional[int]
    teachers: List[Teacher]
