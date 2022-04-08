from sqlmodel import Session, select
from src.db import School, Subject
from src.scrapers import get_subjects, get_description, request


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Cache
schools_cache: dict[str, School] = {}
errors: set[str] = set()


async def search_catalogo_code(base_code: str, db_session: Session, catalogo_session) -> None:
    "Search code in Catalogo and save subjects to DB"
    print(f"Searching {base_code}")

    try:
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
            school = schools_cache.get(s["school_name"])
            if not school:
                school_query = select(School).where(School.name == s["school_name"])
                school = db_session.exec(school_query).one_or_none()
                if not school:
                    school = School(name=s["school_name"])
                    db_session.add(school)
            subject.school = school

            # Save to DB and cache
            try:
                db_session.add(subject)
                db_session.commit()
            except:
                db_session.rollback()
                errors.add(s["code"])
            else:
                schools_cache[s["school_name"]] = school

    except:
        errors.add(base_code)


async def get_full_catalogo(db_session: Session) -> None:
    # Search all
    async with request.catalogo() as catalogo_session:
        for a in LETTERS:
            for b in LETTERS:
                for c in LETTERS:
                    base_code = a + b + c
                    await search_catalogo_code(base_code, db_session, catalogo_session)

    # Retry errors with new session
    async with request.catalogo() as catalogo_session:
        initial_errors: set[str] = errors.copy()
        errors.clear()
        for base_code in initial_errors:
            await search_catalogo_code(base_code, db_session, catalogo_session)
        
        print("Errors", errors)
