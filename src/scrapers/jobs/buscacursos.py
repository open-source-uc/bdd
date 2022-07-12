from typing import Dict, Optional, Set, Union

from sqlmodel import Session, delete, select

from ...db import (
    Campus,
    ClassSchedule,
    Course,
    CoursesTeachers,
    DayEnum,
    PeriodEnum,
    Subject,
    Teacher,
    Term,
)
from .. import request
from ..buscacursos import get_courses
from . import log
from .catalogo import search_additional_info, search_catalogo_code
from .code_iterator import CodeIterator

MAX_BC = 50

# Cache
term_id: Union[int, None] = None
courses_cache: Set[str] = set()
campus_cache: Dict[str, Optional[int]] = {}
subject_cache: Dict[str, Optional[int]] = {}
errors: Set[str] = set()


async def search_bc_code(
    base_code: str, year: int, semester: int, db_session: Session, bc_session
) -> int:
    "Search code in Buscacursos and save courses to DB"
    log.info("Searching %s in Buscacursos", base_code)
    global term_id

    try:
        courses = await get_courses(base_code, year, semester, session=bc_session)
        for c in courses:
            # Check cache
            course_section_term = c["code"] + str(c["section"]) + str(term_id)
            if course_section_term in courses_cache:
                continue

            log.info("Found %s-%i", c["code"], c["section"])
            try:
                # Get or create instance
                course_query = (
                    select(Course)
                    .join(Subject)
                    .where(
                        Course.section == c["section"],
                        Course.term_id == term_id,
                        Subject.code == c["code"],
                        Course.subject_id == Subject.id,
                    )
                )
                course: Course = db_session.exec(course_query).one_or_none()
                if not course:
                    course = Course()

                # Set Subject
                subject_id: Optional[int] = subject_cache.get(c["code"])
                if not subject_id:
                    subject_query = select(Subject).where(Subject.code == c["code"])
                    subject = db_session.exec(subject_query).one_or_none()
                    if not subject:
                        async with request.catalogo() as catalogo_session:
                            await search_catalogo_code(c["code"], db_session, catalogo_session)
                            await search_additional_info(c["code"], db_session, catalogo_session)
                        subject = db_session.exec(subject_query).one_or_none()
                    subject_id = subject.id
                    subject_cache[c["code"]] = subject_id
                course.subject_id = subject_id

                # Fill data
                course.term_id = term_id
                course.nrc = c["ncr"]
                course.section = c["section"]
                course.format = c["format"]
                course.category = c["category"]
                course.is_removable = c["allows_withdraw"]
                course.is_english = c["is_in_english"]
                course.total_quota = c["total_vacancy"]
                course.fg_area = c["fg_area"]
                course.need_special_aproval = c["requires_special_approval"]
                course.available_quota = c["available_vacancy"]

                # Set Campus
                campus_id = campus_cache.get(c["campus"])
                if not campus_id:
                    campus_query = select(Campus).where(Campus.name == c["campus"])
                    campus = db_session.exec(campus_query).one_or_none()
                    if not campus:
                        campus = Campus(name=c["campus"])
                        try:
                            db_session.add(campus)
                            db_session.commit()
                        except Exception:
                            log.error("Cannot save campus: %s", c["campus"], exc_info=True)
                            errors.add(c["code"])
                            db_session.rollback()
                            continue
                        else:
                            campus_cache[c["campus"]] = campus_id

                    campus_id = campus.id
                course.campus_id = campus_id

                # Set Teachers
                if course.id is not None:
                    db_session.exec(
                        delete(CoursesTeachers).where(CoursesTeachers.course_id == course.id)
                    )
                teachers = []
                for teacher_name in c["teachers"]:
                    teacher = db_session.exec(
                        select(Teacher).where(Teacher.name == teacher_name)
                    ).one_or_none()
                    if not teacher:
                        teacher = Teacher(name=teacher_name)
                        try:
                            db_session.add(teacher)
                            db_session.commit()
                        except Exception:
                            log.error("Cannot save teacher: %s", teacher_name, exc_info=True)
                            errors.add(c["code"])
                            db_session.rollback()
                            continue

                        teachers.append(teacher)
                course.teachers = teachers

                # Set schedule if changed (or new)
                if course.schedule_summary != str(c["schedule"]):
                    course.schedule_summary = str(c["schedule"])

                    if course.id is not None:
                        db_session.exec(
                            delete(ClassSchedule).where(ClassSchedule.course_id == course.id)
                        )

                    schedule_list = []
                    for schedule_part_data in c["schedule"]:
                        day, module = schedule_part_data["module"]
                        schedule_part = ClassSchedule(
                            day=DayEnum(day),
                            module=int(module),
                            classroom=schedule_part_data["classroom"],
                            type=schedule_part_data["type"],
                        )
                        schedule_list.append(schedule_part)
                    course.schedule = schedule_list

                # Save to DB and cache
                try:
                    db_session.add(course)
                    db_session.commit()
                except Exception:
                    log.error("Cannot save %s-%i", c["code"], c["section"], exc_info=True)
                    errors.add(c["code"])
                    db_session.rollback()
                else:
                    courses_cache.add(course_section_term)

            except Exception:
                log.error("Cannot process %s-%i", c["code"], c["section"], exc_info=True)
                errors.add(c["code"])

        return len(courses)

    except Exception:
        log.error("Cannot process search %s", base_code, exc_info=True)
        errors.add(base_code)
        return 0


async def get_full_buscacursos(db_session: Session, year: int, semester: int) -> None:
    # Set term
    period = PeriodEnum.from_int(semester)
    term_query = select(Term).where(Term.year == year, Term.period == period)
    term = db_session.exec(term_query).one_or_none()
    if not term:
        term = Term(year=year, period=period)
        db_session.add(term)
        db_session.commit()
    global term_id
    term_id = term.id

    # Search all
    async with request.buscacursos() as bc_session:
        code_generator = CodeIterator()
        for code in code_generator:
            if await search_bc_code(code, year, semester, db_session, bc_session) >= MAX_BC:
                code_generator.add_depth()

    # Retry errors with new session
    async with request.buscacursos() as bc_session:
        initial_errors: Set[str] = errors.copy()
        errors.clear()
        for code in initial_errors:
            await search_bc_code(code, year, semester, db_session, bc_session)

    if len(errors) != 0:
        log.error("Errors %s", ", ".join(errors))
