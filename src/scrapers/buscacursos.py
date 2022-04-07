"""
Scrapper del https://buscacursos.uc.cl/
------------------------------------

Funciona de manera asyncrona, para ser utilizada en la API.
Requiere de una sesión de `aiohttp` con `base_url`.

```py
from aiohttp import ClientSession

async def main():
    async with ClientSession(base_url="https://buscacursos.uc.cl/") as session:
        print(await get_subjects("IIC2233", 2021, 1, session=session))
        print(await get_subjects("MAT1630", 2021, 1, session=session))

asyncio.run(main())
```
"""

import itertools
import re
from typing import TYPE_CHECKING

import bs4

from .utils import (clean_text, gather_routines, run_parse_strategy,
                    tag_to_int_value)

if TYPE_CHECKING:
    from .types import ScrappedCourse
    from .utils import ParseStrategy, Session

NON_EMPTY_TEXT_RE = re.compile(r"(.|\s)*\S(.|\s)*")
ACADEMIC_UNIT_FINDER = {"attrs": {"style": None, "class": None}, "text": NON_EMPTY_TEXT_RE}

MISSING_CLASSROM_RE = re.compile(r"\(?Por Asignar\(?")


def parse_schedule_row(row: "bs4.element.Tag"):
    packed_data: "list[str]" = [r.text.strip() for r in row.find_all("td")]
    module_schedule, module_type, classroom, *_ = packed_data
    days_raw, hours_raw = module_schedule.split(":")

    if not (days_raw or hours_raw):
        return []

    actual_classroom = None if MISSING_CLASSROM_RE.match(classroom) else classroom

    return [
        {"classroom": actual_classroom, "type": module_type, "module": f"{d}{h}"}
        for d, h in itertools.product(days_raw.split("-"), hours_raw.split(","))
    ]


def parse_schedule(row_value_tag: "bs4.element.Tag"):
    schedule_table = row_value_tag.find("table")
    schedule = []
    if isinstance(schedule_table, bs4.element.Tag):
        for module_row in schedule_table.find_all("tr"):
            schedule.extend(parse_schedule_row(module_row))
        return schedule


MISSING_TEACHERS_RE = re.compile(r"Sin Profesores")


def parse_teachers(row_value_tag: "bs4.element.Tag"):
    raw_info = row_value_tag.text.strip()
    if not MISSING_TEACHERS_RE.match(raw_info):
        return raw_info.split(", ")


COLUMNS_STRATEGIES: "ParseStrategy" = {
    "ncr": clean_text,
    "code": clean_text,
    "allows_withdraw": lambda n: clean_text(n) == "SI",
    "is_in_english": lambda n: clean_text(n) == "SI",
    "section": tag_to_int_value,
    "requires_special_approval": lambda n: clean_text(n) == "SI",
    "fg_area": clean_text,
    "format": clean_text,
    "category": clean_text,
    "name": clean_text,
    "teachers": parse_teachers,
    "campus": clean_text,
    "credits": tag_to_int_value,
    "total_vacancy": tag_to_int_value,
    "available_vacancy": tag_to_int_value,
    "reserved_vacancy": None,
    "schedule": parse_schedule,
    "add_to_calendar": None,
}


async def parse_row(row: "bs4.element.Tag"):
    data = {}
    faculty_tag = row.find_previous_sibling(**ACADEMIC_UNIT_FINDER)
    if isinstance(faculty_tag, bs4.element.Tag):
        data["faculty"] = faculty_tag.text.strip()
    return data | run_parse_strategy(COLUMNS_STRATEGIES, row.findChildren("td", recursive=False))


MATCH_RESULT_ROW = {"class": re.compile("resultados")}


async def get_courses_raw(session: "Session", **params) -> "list[ScrappedCourse]":
    "Obtiene los cursos utilizando, usando los parámetros del URL"
    async with session.get("/", params=params) as response:
        body = await response.read()
        soup = bs4.BeautifulSoup(body, "lxml")
        results = soup.find_all("tr", MATCH_RESULT_ROW)
        if not results:
            return []
        return await gather_routines([parse_row(row) for row in results])


async def get_courses(code: "str", year: "int", semester: int, *, session: "Session"):
    "Obtiene los cursos por la sigla, año y semestre (TAV == 3)"
    return await get_courses_raw(session, cxml_semestre=f"{year}-{semester}", cxml_sigla=code)


async def get_available_terms(session: "Session"):
    async with session.post("/") as response:
        body = await response.read()
    soup = bs4.BeautifulSoup(body, "lxml")

    academic_period_selector = soup.find("select", {"name": "cxml_semestre"})
    academic_periods: "list[tuple[int, int]]" = []
    if isinstance(academic_period_selector, bs4.element.Tag):
        for option in academic_period_selector.findChildren("option"):
            if isinstance(option, bs4.element.Tag):
                year, period = option.attrs["value"].split("-")
                academic_periods.append((int(year), int(period)))
    return academic_periods
