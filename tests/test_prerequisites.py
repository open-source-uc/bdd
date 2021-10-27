from dotenv import load_dotenv
from sqlmodel.sql.expression import select

load_dotenv()

from sqlmodel import Session, delete
from src.db import engine, Subject


def test_prerequisites():
    # TODO: usar db de testing

    with Session(engine) as session:
        s1 = Subject(name="ejemplo", code="EJ0000")
        ra_1 = Subject(name="ra-1", code="ERA1")
        ra_2 = Subject(name="ra-2", code="ERA2")
        rb_1 = Subject(name="rb-1", code="ERB1")

        s1.set_prerequisites([[ra_1, ra_2], [rb_1]])
        session.add(s1)

        s1_db = session.exec(select(Subject).where(Subject.code == "EJ0000")).one()
        prerequisites = s1_db.prerequisites
        assert len(prerequisites) == 2
        assert {len(prerequisites[i].child_and_groups) for i in (0, 1)} == {1, 2}

        delete(Subject).where(Subject.code.in_(["EJ0000", "ERA1", "ERA2", "ERB1"]))  # type: ignore
