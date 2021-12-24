from typing import TYPE_CHECKING, Callable, Any, Coroutine, Optional, Literal

import re
import asyncio

if TYPE_CHECKING:
    import bs4
    from aiohttp import ClientSession as Session

    Semester = Literal[1, 2, 3]
    ParseStrategy = dict[str, Optional[Callable[[bs4.element.Tag], Any]]]


def clean_text(tag: "bs4.element.Tag") -> "str":
    "Limpia el texto de un tag"
    return re.sub(r"\s{2,}", " ", tag.text).strip()


async def gather_routines(tasks: list[Coroutine]):
    "Wrapper de asyncio.gather, que utiliza listas en vez de tuplas"
    return list(await asyncio.gather(*tasks))


def run_parse_strategy(ps: "ParseStrategy", tags: "list[bs4.element.Tag]"):
    """
    Corre funciones para obtener los datos en una lista de tags.
    Por ejemplo:
    ```
    >>> # Notar que `tags` no tiene información del nombre correspondiente
    >>> tags = [<h1>Hola mundo</h1>, <p>A,B,C<p>]  # pseudo código
    >>> ps = {"titulo": lambda p: p.text, "elementos": lambda p: p.text.split() }
    >>> run_parse_strategy(ps, tags)
    {"titulo": "Hola mundo", "elementos": ["A", "B", "C"] }
    ```
    """
    data: "dict[str, Any]" = {}
    # Esto asume que el diccionario es ordenado (Python ^3.8)
    for value_tag, col_name in zip(tags, ps):
        parse_fn = ps.get(col_name, None)
        if parse_fn is not None:
            result = parse_fn(value_tag)
            if result is not None:
                data[col_name] = result
    return data