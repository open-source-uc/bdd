from typing import Optional, TypedDict, List, Tuple


class ScrappedSubject(TypedDict):
    school_name: str
    code: str
    name: str
    level: str
    credits: int
    is_active: bool
    description: Optional[str]
    syllabus: str
    requirements: List[List[str]]
    equivalences: List[str]
    relationship: str
    restrictions: List[Tuple[str, str]]


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
    schedule: List[ScheduleItem]
    section: int
    teachers: List[str]
    total_vacancy: int
