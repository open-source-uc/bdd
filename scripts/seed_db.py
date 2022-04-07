from dotenv import load_dotenv
import os, sys

sys.path.insert(0, os.getcwd())
load_dotenv()

from sqlmodel import Session, delete, select
from src.db import (
    engine,
    create_db,
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
from src.scrapers import get_courses, get_subjects, get_description, request
import asyncio
from time import time

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = range(10)

# Cache
schools: dict[str, School] = {}


async def search_catalogo_code(base_code: str, db_session: Session, catalogo_session):
    print(f"Searching {base_code}")
    subjects = await get_subjects(base_code, session=catalogo_session)
    for s in subjects:
        print(f"Found: {s['code']}: {s['name']}")

        # Get or create instance
        subject_query = select(Subject).where(Subject.code == s["code"])
        subject: Subject = db_session.exec(subject_query).one_or_none()
        if not subject:
            subject = Subject()

        # Fill data
        subject.name = s["name"]
        subject.code = s["code"]
        subject.credits = s["credits"]
        subject.requirements_relation = s["relationship"]
        subject.restrictions = ",".join(["=".join(r) for r in s["restrictions"]])
        subject.syllabus = s["syllabus"]
        subject.academic_level = s["level"]
        subject.description = get_description(s["syllabus"])

        # Check school (use cache)
        global schools
        school = schools.get(s["school_name"])
        if not school:
            school_query = select(School).where(School.name == s["school_name"])
            school = db_session.exec(school_query).one_or_none()
            if not school:
                school = School(name=s["school_name"])
                db_session.add(school)
        subject.school = school

        # Save to DB and cache
        db_session.add(subject)
        try:
            db_session.commit()
            schools[s["school_name"]] = school
        except:
            db_session.rollback()


async def get_full_catalogo(db_session: Session) -> None:
    init_time = time()
    errors = []
    async with request.catalogo() as catalogo_session:
        for a in LETTERS:
            for b in LETTERS:
                for c in LETTERS:
                    base_code = a + b + c
                    try:
                        await search_catalogo_code(base_code, db_session, catalogo_session)

                    except:
                        print("Error at", base_code, sys.exc_info())
                        errors.append(base_code)

    print(f"Time elapsed: {(time() - init_time) / 60:1f} minutes")
    print("Errors", errors)


# Start script
create_db()

with Session(engine) as session:
    asyncio.run(get_full_catalogo(session))
