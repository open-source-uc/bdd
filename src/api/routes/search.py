from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ...db import (
    Campus,
    ClassSchedule,
    Course,
    DayEnum,
    Faculty,
    PeriodEnum,
    School,
    Subject,
    Teacher,
    Term,
)
from ...scrapers import get_available_terms, get_courses, get_subjects, request
from ..utils import get_db

search_router = APIRouter()


async def get_or_create_subject(code: str, db: Session):
    subject = db.exec(select(Subject).where(Subject.code == code)).one_or_none()
    print(subject)
    if subject:
        return subject

    print(f"Searching subject: code={code}")

    async with request.catalogo() as session:
        scrapped_subjects_data = await get_subjects(code, session=session)

    subjects: "list[Subject]" = []
    for subject_data in scrapped_subjects_data:
        new_subject = Subject(
            name=subject_data["name"],
            code=subject_data["code"],
            credits=subject_data["credits"],
            description=subject_data.get("description"),
            requirements_relation=subject_data["relationship"],
            restrictions="".join(["=".join(r) for r in subject_data["restrictions"]]),
            syllabus=subject_data["syllabus"],
            academic_level=subject_data["level"],
        )

        # Añadir escuela si no existe
        school_query = select(School).where(School.name == subject_data["school_name"])
        school = db.exec(school_query).one_or_none()
        if not school:
            school = School(name=subject_data["school_name"])
            db.add(school)
        new_subject.school = school

        # Encontrar los pre-requisitos
        prerequisites: "list[list[Subject]]" = []
        for or_groups in subject_data["requirements"]:
            or_group_list: "list[Subject]" = []
            for course_code in or_groups:
                requirement_course = await get_or_create_subject(course_code, db)
                if not requirement_course:
                    raise ValueError(f"Subject {course_code} should exists, but it doesn't")
                or_group_list.append(requirement_course)
            prerequisites.append(or_group_list)
        new_subject.set_prerequisites(prerequisites)

        # Guardar resultado
        subjects.append(new_subject)
        db.add(new_subject)

    # Se retorna un ramo si el código es el buscado
    return next((s for s in subjects if s.code == code), None)


async def get_or_create_academic_term(year: int, period: PeriodEnum, db: Session):
    term = db.exec(select(Term).where(Term.year == year and Term.period == period)).one_or_none()
    if term:
        return term

    print(f"Searching academic term: year={year}, period={term}")
    terms: "list[Term]" = []
    async with request.buscacursos() as session:
        for (new_term_year, new_term_period) in await get_available_terms(session):
            new_term = Term(year=new_term_year, period=PeriodEnum.from_int(new_term_period))
            db.add(new_term)
            terms.append(new_term)

    # Se retorna un periodo academico si existe en los resultados
    return next((t for t in terms if t.year == year and t.period == period), None)


def get_or_create_campus(campus_name: str, db: Session):
    campus = db.exec(select(Campus).where(Campus.name == campus_name)).one_or_none()
    if not campus:
        campus = Campus(name=campus_name)
        db.add(campus)
    return campus


def get_or_crate_faculty(faculty_name: str, db: Session):
    faculty = db.exec(select(Faculty).where(Faculty.name == faculty_name)).one_or_none()
    if not faculty:
        faculty = Faculty(name=faculty_name)
        db.add(faculty)
    return faculty


def get_or_create_teachers(teachers_names: list[str], db: Session):
    teachers: list[Teacher] = []
    for teacher_name in teachers_names:
        teacher = db.exec(select(Teacher).where(Teacher.name == teacher_name)).one_or_none()
        if not teacher:
            teacher = Teacher(name=teacher_name)
            teachers.append(teacher)
            db.add(teacher)
    return teachers


async def get_or_create_courses(subject: Subject, term: Term, db: Session):
    courses_query = (
        select(Course)
        .join(Term)
        .where(Term.year == term.year and Term.period == term.period)
        .join(Subject)
        .where(Subject.code == subject.code)
    )
    courses = db.exec(courses_query).all()
    if courses:
        return courses

    print(f"Seraching for courses: code={subject.code}, year={term.year}, period={term.period}")

    created_courses = []
    async with request.buscacursos() as session:
        courses_data = await get_courses(subject.code, term.year, int(term.period), session=session)
        for new_course_data in courses_data:
            new_course = Course(
                subject_id=subject.id,
                term_id=term.id,
                nrc=new_course_data["ncr"],
                section=new_course_data["section"],
                format=new_course_data["format"],
                category=new_course_data["category"],
                is_removable=new_course_data["allows_withdraw"],
                is_english=new_course_data["is_in_english"],
                schedule_summary=str(new_course_data["schedule"]),
                total_quota=new_course_data["total_vacancy"],
                fg_area=new_course_data["fg_area"],
                need_special_aproval=new_course_data["requires_special_approval"],
                available_quota=new_course_data["available_vacancy"],
            )

            new_course.campus = get_or_create_campus(new_course_data["campus"], db)
            new_course.faculty = get_or_crate_faculty(new_course_data["faculty"], db)
            new_course.teachers = get_or_create_teachers(new_course_data["teachers"], db)

            for schedule_part_data in new_course_data["schedule"]:
                day, module = schedule_part_data["module"]
                schedule_part = ClassSchedule(
                    day=DayEnum(day),
                    module=int(module),
                    classroom=schedule_part_data["classroom"],
                    type=schedule_part_data["type"],
                )
                new_course.schedule.append(schedule_part)

            created_courses.append(new_course)
            db.add(new_course)

    return created_courses


@search_router.get("/")
async def search_or_get(code: str, year: int, period: PeriodEnum, *, db: Session = Depends(get_db)):
    """
    Este endpoint esta creado para la obtención de datos.
    Las respuestas de las consultas pueden demorar mucho si no hay datos buscados.
    """
    term = await get_or_create_academic_term(year, period, db)
    if not term:
        raise HTTPException(404, "Academic period not found")

    subject = await get_or_create_subject(code, db)
    if not subject:
        raise HTTPException(404, "Subject not found")

    courses = await get_or_create_courses(subject, term, db)

    return {"courses": courses, "subject": subject}
