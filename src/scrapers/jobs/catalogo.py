from sqlmodel import Session, select
from .code_iterator import CodeIterator
from ...db import School, Subject
from ..catalogo import get_subjects, get_additional_info, get_syllabus
from ..description import get_description
from .. import request
from . import log


# Cache
schools_cache: dict[str, int] = {}
subjects_cache: set[str] = set()
errors: set[str] = set()

MAX_CATALOGO = 1000


async def search_catalogo_code(base_code: str, db_session: Session, catalogo_session) -> int:
    "Search code in Catalogo and save subjects to DB"
    log.info("Searching %s in Catalogo", base_code)

    try:
        subjects = await get_subjects(
            base_code, session=catalogo_session, all_subjects=True, all_info=False
        )
        for s in subjects:
            if s["code"] in subjects_cache:
                continue

            log.info("Found %s: %s", s["code"], s["name"])
            try:
                # Get or create instance
                subject_query = select(Subject).where(Subject.code == s["code"])
                subject: Subject = db_session.exec(subject_query).one_or_none()
                if not subject:
                    subject = Subject()

                # Fill data
                subject.name = s["name"]
                subject.code = s["code"]
                subject.credits = s["credits"]
                subject.academic_level = s["level"]
                subject.description = s.get("description")
                subject.is_active = s["is_active"]

                # Check school (use cache)
                school_id = schools_cache.get(s["school_name"])
                if not school_id:
                    school_query = select(School).where(School.name == s["school_name"])
                    school = db_session.exec(school_query).one_or_none()
                    if not school:
                        school = School(name=s["school_name"])
                        db_session.add(school)
                        try:
                            db_session.add(school)
                            db_session.commit()
                        except Exception:
                            log.error("Cannot save school: %s", s["school_name"], exc_info=True)
                            errors.add(s["code"])
                            db_session.rollback()
                            continue
                        else:
                            schools_cache[s["school_name"]] = school_id

                    school_id = school.id
                subject.school_id = school_id

                # Save to DB and cache
                try:
                    db_session.add(subject)
                    db_session.commit()
                except Exception:
                    log.error("Cannot save %s", s["code"], exc_info=True)
                    errors.add(s["code"])
                    db_session.rollback()
                else:
                    subjects_cache.add(s["code"])

            except Exception:
                log.error("Cannot process %s", s["code"], exc_info=True)
                errors.add(s["code"])

        return len(subjects)

    except Exception:
        log.error("Cannot process search %s", base_code, exc_info=True)
        errors.add(base_code)
        return 0


async def search_additional_info(code: str, db_session: Session, catalogo_session) -> None:
    "Search code requirements and syllabus in Catalogo and save to DB"
    log.info("Searching %s in Catalogo", code)

    try:
        data = await get_additional_info(code, session=catalogo_session)
        syllabus = await get_syllabus(code, session=catalogo_session).get("syllabus")

        subject: Subject = db_session.exec(
            select(Subject).where(Subject.code == code)
        ).one_or_none()
        if not subject:
            errors.add(code)
            log.error("Discovered %s not found in DB", code)
            return

        subject.syllabus = syllabus
        if subject.description is None:
            subject.description = get_description(syllabus)

        subject.need_all_requirements = data["relationship"]
        subject.restrictions = ",".join(["=".join(r) for r in data["restrictions"]])
        subject.prerequisites_raw = data["prerequisites_raw"]
        # TODO: equivalencies and prerequistes many-to-many

        try:
            db_session.add(subject)
            db_session.commit()
        except Exception:
            log.error("Cannot save %s", code, exc_info=True)
            errors.add(code)
            db_session.rollback()
    
    except Exception:
        log.error("Cannot get requirements and syllabus for %s", code, exc_info=True)
        errors.add(code)


async def get_full_catalogo(db_session: Session) -> None:
    # Search all
    async with request.catalogo() as catalogo_session:
        code_generator = CodeIterator()
        for code in code_generator:
            if await search_catalogo_code(code, db_session, catalogo_session) >= MAX_CATALOGO:
                code_generator.add_depth()

    # Retry errors with new session
    async with request.catalogo() as catalogo_session:
        initial_errors: set[str] = errors.copy()
        errors.clear()
        for code in initial_errors:
            await search_catalogo_code(code, db_session, catalogo_session)

    if len(errors) != 0:
        log.error("Discover errors %s", ", ".join(errors))
        errors.clear()

    # Get requirements and syllabus for discovered subjects
    async with request.catalogo() as catalogo_session:
        for code in subjects_cache:
            await search_additional_info(code, db_session, catalogo_session)

    # Retry errors with new session
    async with request.catalogo() as catalogo_session:
        initial_errors: set[str] = errors.copy()
        errors.clear()
        for code in initial_errors:
            await search_additional_info(code, db_session, catalogo_session)
    
    if len(errors) != 0:
        log.error("Requirements and syllabus errors %s", ", ".join(errors))
