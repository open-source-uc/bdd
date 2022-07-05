"""
Scrapper del https://catalogo.uc.cl/
------------------------------------

Funciona de manera asyncrona, para ser utilizada en la API.
Requiere de una sesión de `aiohttp` con `base_url`.

```py
from aiohttp import ClientSession

async def main():
    async with ClientSession(base_url="https://catalogo.uc.cl/") as session:
        print(await get_subjects("IIC2233", session=session))
        print(await get_subjects("MAT1630", session=session))

asyncio.run(main())
```
"""

import html
import re
from sympy import Symbol, symbols
from sympy.logic.boolalg import And, Or, to_dnf, simplify_logic
from typing import TYPE_CHECKING, Callable, Optional, cast

import bs4

from .utils import clean_text, gather_routines, run_parse_strategy, tag_to_int_value

if TYPE_CHECKING:
    from .types import ScrappedSubject
    from .utils import ParseStrategy, Session


DESCRIPTION_RE = re.compile(r"Descripción:\s*(.*)\s*$")


def parse_description(value_node: "bs4.element.Tag") -> "Optional[str]":
    text = value_node.get_text(separator=" ")
    match = DESCRIPTION_RE.search(text)
    if match:
        return match.group(1).strip()
    return None


COLUMNS_STRATEGIES: "ParseStrategy" = {
    "school_name": clean_text,
    "code": clean_text,
    "name": clean_text,
    "level": clean_text,
    "credits": tag_to_int_value,
    "is_active": lambda n: clean_text(n) == "Vigente",
    "description": parse_description,
    "requirements": None,
    "program": None,
    "bc": None,
}

BASE_SUBJECT_PARAMS = {
    "ItemId": 378,
    "option": "com_catalogo",
    "view": "cursoslist",
    "tmpl": "component",
}

BASE_REQUIREMENTS_PARAMS = {"view": "requisitos", "tmpl": "component"}


def _finder_by_text_table_key(key: str):
    strign_to_search = key.encode().decode("utf-8", "xmlcharrefreplace")

    def finder(element: "bs4.element.Tag"):
        if element.name != "strong":
            return False
        return strign_to_search in html.unescape(clean_text(element))

    return finder


def find_text_by_table_key(soup: "bs4.BeautifulSoup", key: "str"):
    element = soup.find(_finder_by_text_table_key(key))
    if element and element.parent and element.parent.next_sibling:
        return element.parent.next_sibling.text.strip()
    return None


def get_formula(elements_list: list[str], req_dict: dict[str, Symbol]):
    relation_func: Callable = None
    variables = []
    while len(elements_list) != 0:
        el = elements_list.pop(0)
        if el == "":
            continue
        elif el == '(':
            variables.append(get_formula(elements_list, req_dict))
        elif el == ")":
            if relation_func is not None:
                return relation_func(*variables)
            return variables[0]
        elif el == "y":
            relation_func = And
        elif el == "o":
            relation_func = Or
        else:
            variables.append(req_dict[el])

    if relation_func is not None:
        return relation_func(*variables)
    return variables[0]


def parse_requirements_groups(requirements_text: str):
    # Los requisitos tienen forma "(A y B) o (A y C) o D(c)"
    requirements = []
    if requirements_text != "No tiene":
        # Convertir a DNF (suma de productos)
        req_parts = (requirements_text
            .replace("(c)", "c")
            .replace("(", "#(#")
            .replace(")", "#)#")
            .replace(" ", "#")
            .split("#")
        )

        req_list = [x for x in set(req_parts) if x not in ["", "y", "o", "(", ")"]]
        syms = symbols(":" + str(len(req_list)))
        req_dict = {}
        for i, code in enumerate(req_list):
            req_dict[code] = syms[i]

        formula = to_dnf(get_formula(req_parts, req_dict))

        for group_str in str(formula).split("|"):
            group = []
            group_syms = group_str.strip("( )").split(" & ")
            for sym_name in group_syms:
                group.append(req_list[int(sym_name)])
            requirements.append(group)
            
    return requirements


def parse_relationship(relationship_text: str):
    return relationship_text == "y"


RESTRICTIONS_RE = re.compile(r"\(\s*([^\(]*?)\s*=\s*([^\)]*?)\s*\)")


def parse_restrictions(restrictions_text: str):
    if restrictions_text == "No tiene":
        return []
    return RESTRICTIONS_RE.findall(restrictions_text)


async def get_additional_info(code: str, *, session: "Session"):
    params = BASE_REQUIREMENTS_PARAMS | {"sigla": code}
    async with session.get("/index.php", params=params) as response:
        body = await response.read()
    soup = bs4.BeautifulSoup(body, "lxml")
    data = {}

    # TODO: limpiar esto
    requirements_text = find_text_by_table_key(soup, "Prerrequisitos")
    if requirements_text:
        data["prerequisites_raw"] = requirements_text
        data["requirements"] = parse_requirements_groups(requirements_text)

    equivalencies_text = find_text_by_table_key(soup, "Equivalencias")
    if equivalencies_text:
        data["equivalencies_raw"] = equivalencies_text
        data["equivalencies"] = parse_requirements_groups(equivalencies_text)

    relationship_text = find_text_by_table_key(soup, "Relación")
    if relationship_text:
        data["relationship"] = parse_relationship(relationship_text)

    restrictions_text = find_text_by_table_key(soup, "Restricciones")
    if restrictions_text:
        data["restrictions"] = parse_restrictions(restrictions_text)

    return data


SYLLABUS_BASE_PARAMS = {"view": "programa", "tmpl": "component"}


async def get_syllabus(code: str, *, session: "Session"):
    params = SYLLABUS_BASE_PARAMS | {"sigla": code}
    async with session.get("/index.php", params=params) as response:
        body = await response.read()
    soup = bs4.BeautifulSoup(body, "lxml")
    syllabus = soup.select_one("div > pre")
    if syllabus:
        return {"syllabus": syllabus.text.strip().replace("\r\n", "\n")}
    return {}


async def parse_row(row: "bs4.element.Tag", session: "Session", all_info: bool):
    data = run_parse_strategy(COLUMNS_STRATEGIES, row.findChildren("td", recursive=False))
    code = data.get("code")
    if all_info and code is not None:
        data |= await get_additional_info(code, session=session)
        data |= await get_syllabus(code, session=session)
    return data


async def get_subjects(
    code: str, *, session: "Session", all_subjects: bool = True, all_info: bool = True
) -> "list[ScrappedSubject]":
    "Obtiene los ramos por su sigla"
    params = BASE_SUBJECT_PARAMS | {"sigla": code, "vigencia": 2 * int(all_subjects)}
    async with session.post("/index.php", params=params) as response:
        body = await response.read()
    soup = bs4.BeautifulSoup(body, "lxml")
    return await gather_routines(
        [parse_row(row, session, all_info) for row in soup.select("tbody > tr")]
    )
