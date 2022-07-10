from typing import Dict, Optional, Set

from sqlmodel import Session, select

from scripts.fullscrapers.code_iterator import CodeIterator
from src.db import School, Subject
from src.db.schema import RequirementRelationEnum
from src.scrapers import get_description, get_subjects, request

from . import log

# Cache
schools_cache: Dict[str, Optional[int]] = {}
subjects_cache: Set[str] = set()
errors: Set[str] = set()

MAX_CATALOGO = 1000


async def search_catalogo_code(base_code: str, db_session: Session, catalogo_session) -> int:
    "Search code in Catalogo and save subjects to DB"
    log.info("Searching %s in Catalogo", base_code)

    try:
        subjects = await get_subjects(base_code, session=catalogo_session)
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
                subject.requirements_relation = RequirementRelationEnum.from_catalogo(
                    s["relationship"]
                )
                subject.restrictions = ",".join(["=".join(r) for r in s["restrictions"]])
                subject.syllabus = s["syllabus"]
                subject.academic_level = s["level"]
                subject.description = get_description(s["syllabus"])

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


async def get_full_catalogo(db_session: Session) -> None:
    # Search all
    async with request.catalogo() as catalogo_session:
        code_generator = CodeIterator()
        for code in code_generator:
            if await search_catalogo_code(code, db_session, catalogo_session) >= MAX_CATALOGO:
                code_generator.add_depth()

    # Retry errors with new session
    async with request.catalogo() as catalogo_session:
        initial_errors: Set[str] = errors.copy()
        errors.clear()
        for code in initial_errors:
            await search_catalogo_code(code, db_session, catalogo_session)

    if len(errors) != 0:
        log.error("Errors %s", ", ".join(errors))
