from typing import Optional, TypedDict


class ScrappedSubject(TypedDict):
    school_name: str
    code: str
    name: str
    level: str
    credits: int
    is_active: bool
    description: Optional[str]
    syllabus: str
    requirements: list[list[str]]
    prerequisites_raw: str
    equivalencies: list[list[str]]
    equivalencies_raw: str
    relationship: str
    restrictions: list[tuple[str, str]]


class ScheduleItem(TypedDict):
    classroom: str
    module: str
    type: str


class ScrappedCourse(TypedDict):
    academic_unit: str
    allows_withdraw: bool
    available_vacancy: int
    campus: str
    category: str
    code: str
    credits: int
    school: str
    fg_area: str
    format: str
    is_in_english: bool
    name: str
    ncr: str
    requires_special_approval: bool
    reserved_vacancy: str
    schedule: list[ScheduleItem]
    section: int
    teachers: list[str]
    total_vacancy: int
