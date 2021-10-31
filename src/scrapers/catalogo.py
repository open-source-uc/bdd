from pathlib import Path
import csv
from typing import Literal, NamedTuple, Optional
import bs4
import re
from utils import Requester, clean_text
import html

CATALOGO_REQUESTER = Requester("https://catalogo.uc.cl/")

COLUMNS = {
    "school_name": True,
    "code": True,
    "subject_name": True,
    "level": True,
    "credits": True,
    "is_active": True,
    "description": True,
    "requirements": False,
    "program": False,
    "bc": False,
}


OUT_PATH = Path("data", "subjects")
OUT_PATH.mkdir(parents=True, exist_ok=True)


def get_subjects(code: str, all_subjects: bool = False):
    query = {
        "ItemId": 378,
        "option": "com_catalogo",
        "view": "cursoslist",
        "sigla": code,
        "vigencia": 2 * int(all_subjects),
        "tmpl": "component",
    }
    html_stream = CATALOGO_REQUESTER.request("/index.php", params=query, method="POST")
    soup = bs4.BeautifulSoup(html_stream, "lxml")

    with OUT_PATH.joinpath(code).with_suffix(".csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(filter(COLUMNS.get, COLUMNS))
        for row in soup.select("tbody > tr"):
            row_data = []
            for value_node, col in zip(row.findChildren("td", recursive=False), COLUMNS):
                value_node: bs4.element.Tag
                if col in ["requirements", "program", "bc"]:
                    continue
                elif col == "description":
                    text = value_node.getText(separator=" ")
                    match = re.search(r"Descripción:\s*(.*)\s*$", text)
                    if match:
                        value = match.group(1).strip()
                    else:
                        value = None
                elif col == "is_active":
                    value = clean_text(value_node) == "Vigente"
                else:
                    value = clean_text(value_node)

                row_data.append(value)
            writer.writerow(row_data)


# ------------------------------------------


def find_by_key(string: str):
    strign_to_search = string.encode().decode("utf-8", "xmlcharrefreplace")

    def finder(e: bs4.element.Tag):
        if e.name == "strong":
            return strign_to_search in html.unescape((re.sub(r" +", " ", e.text)))
        return False

    return finder


def _find_key(soup: bs4.BeautifulSoup, string: str):
    e = soup.find(find_by_key(string))
    if e and e.parent and e.parent.next_sibling:
        return e.parent.next_sibling.text.strip()
    return None


class SubjectAdditionalInfo(NamedTuple):
    requirements: Optional[list[list[str]]]
    requirements_raw: Optional[str]
    equivalences: Optional[list[str]]
    equivalences_raw: Optional[str]
    restrictions: Optional[list[tuple[str, str]]]
    restrictions_raw: Optional[str]
    relationship: Optional[str]
    relationship_raw: Optional[str]


def get_subject_additional_info(code: str):
    query = {"view": "requisitos", "tmpl": "component", "sigla": code}
    html_stream = CATALOGO_REQUESTER.request("/index.php", params=query)
    soup = bs4.BeautifulSoup(html_stream, "lxml")

    for br in soup.find_all("br"):
        br.replace_with("")

    print(soup)

    # Requisitos
    requirements_text = _find_key(soup, string="Prerrequisitos")
    requirements: Optional[list[list[str]]] = None
    if requirements_text:
        requirements = []
        if requirements_text != "No tiene":
            or_group = requirements_text.split("o")
            for g in map(str.strip, or_group):
                if g[0] == "(":
                    requirements.append([c.strip() for c in g[1 : len(g) - 1].split("y")])
                else:
                    requirements.append([g])

    # Equivalencias
    equivalences_text = _find_key(soup, string="Equivalencias")
    equivalences: Optional[list[str]] = None
    if equivalences_text:
        if equivalences_text == "No tiene":
            equivalences = []
        else:
            equivalences_data = equivalences_text[1 : len(equivalences_text) - 2].split("o")
            equivalences = [e.strip() for e in equivalences_data]

    # Relación equivalencia y requisitos
    relationship_text = _find_key(soup, string="Relación")
    relationship: Optional[str] = None
    if relationship_text and relationship_text != "No tiene":
        relationship = relationship_text

    # Restricciones
    restrictions_text = _find_key(soup, string="Restricciones")
    restrictions: Optional[list[tuple[str, str]]] = None
    if restrictions_text:
        if restrictions_text == "No tiene":
            restrictions = []
        else:
            restrictions = re.findall(r"\(\s*([^\(]*?)\s*=\s*([^\)]*?)\s*\)", restrictions_text)

    # Retorno
    return SubjectAdditionalInfo(
        requirements=requirements,
        requirements_raw=requirements_text,
        equivalences=equivalences,
        equivalences_raw=equivalences_text,
        restrictions=restrictions,
        restrictions_raw=restrictions_text,
        relationship=relationship,
        relationship_raw=relationship_text,
    )


def get_syllabus(code: str):
    query = {"view": "programa", "tmpl": "component", "sigla": code}
    html_stream = CATALOGO_REQUESTER.request("/index.php", params=query).read()
    soup = bs4.BeautifulSoup(html_stream, "lxml")
    syllabus = soup.select_one("div > pre")
    if syllabus:
        return syllabus.text
    return None


if __name__ == "__main__":
    print(get_syllabus("AGP3131"))
