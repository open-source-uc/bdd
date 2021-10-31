import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from mimetypes import guess_extension
from pathlib import Path
from typing import Union
from urllib.parse import urlparse
import re
import bs4

import requests

CACHE_DIR = Path(".scrapper_cache/")
CACHE_DIR.mkdir(exist_ok=True)

with CACHE_DIR.joinpath(".gitignore").open("w") as ignore_file:
    ignore_file.write("*\n")

CACHE_DB_CONNECTION = sqlite3.connect(CACHE_DIR.joinpath("cache.db"))

CACHE_DB_CONNECTION.execute(
    """
    CREATE TABLE IF NOT EXISTS cache (
        collection TEXT,
        id TEXT,
        expiration REAL,
        file_path TEXT,
        hits INTEGER DEFAULT 0,
        CONSTRAINT pk_cache PRIMARY KEY (collection, id)
    )
"""
)


def clean_text(tag: bs4.element.Tag) -> Union[str, None]:
    return re.sub(r"\s{2,}", " ", tag.text).strip() or None


def dict_to_str(d: dict) -> str:
    return json.dumps(d, sort_keys=True)


def get_file_extention(r: requests.Response):
    return guess_extension(r.headers["content-type"].split(";", maxsplit=1)[0].strip())


def hash_data(*data: str) -> str:
    m_hash = hashlib.md5()
    for element in data:
        m_hash.update(element.encode())
    return m_hash.hexdigest()


class Requester:
    """
    Wrapper de `requests.session.request` que utiliza cache para evitar
    hacer multiples veces la misma request de forma innecesaria.
    ESTO NO DEBE USARSE EN PRODUCCIÓN, Y TAMPOCO SE DEBE UTILIZAR PARA USO
    PERSONAL, PARA EVITAR LA RECOLECCIÓN INNECESARIA DE DATOS QUE YA SON PUBLICOS.
    """

    cache_expire_time = timedelta(days=70)

    def __init__(self, url) -> None:
        parsed_url = urlparse(url)
        self._scheme = parsed_url.scheme
        self._domain = parsed_url.netloc
        self.__db_cursor = CACHE_DB_CONNECTION.cursor()
        self.session = requests.session()
        self.session.max_redirects = 1
        self.session.headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        self.collection_name = self._domain.replace(".", "-")
        CACHE_DIR.joinpath(self.collection_name).mkdir(parents=True, exist_ok=True)

    def __del__(self) -> None:
        # Se asegura que los datos se guarden en disco
        CACHE_DB_CONNECTION.commit()
        self.__db_cursor.close()

    def remove_expired(self):
        self.__db_cursor.execute(
            "DELETE FROM cache WHERE collection=? AND expiration < ?",
            (self.collection_name, datetime.today().timestamp()),
        )

    def find_in_cache(self, identifier: str) -> Union[str, None]:
        self.__db_cursor.execute(
            "SELECT file_path FROM cache WHERE collection=? AND id=?",
            (self.collection_name, identifier),
        )
        hit = self.__db_cursor.fetchone()
        if hit:
            self.__db_cursor.execute(
                "UPDATE cache SET hits = hits + 1 WHERE collection=? AND id=?",
                (self.collection_name, identifier),
            )
            return hit[0]
        return None

    def create_file_path(self, identifier: str, extention: str):
        return CACHE_DIR.joinpath(self.collection_name, str(identifier)).with_suffix(extention)

    def request(self, path: str, *, method: str = "GET", cookies: dict = {}, params: dict = {}):
        """
        Wrapper de `session.get`, pero guardando las respuestas
        para no tener que realizar multiples requests.
        """
        self.remove_expired()

        # Transforma un path/?parametros en schema://domain/path/?parametros
        parsed_path = urlparse(path)
        url = parsed_path._replace(scheme=self._scheme, netloc=self._domain).geturl()

        # Obtiene metadatos de la consulta
        identifier = hash_data(url, path, dict_to_str(cookies), dict_to_str(params))

        # Ve si existe la consulta
        file_path = self.find_in_cache(identifier)
        if not file_path or not Path(file_path).exists():
            # Hace la request si no existe
            response = self.session.request(
                method, url, cookies=cookies, params=params, stream=True
            )

            # Guarda que se realizo una consulta
            expire_datetime = (datetime.today() + self.cache_expire_time).timestamp()
            file_path = self.create_file_path(identifier, get_file_extention(response) or ".txt")
            self.__db_cursor.execute(
                "INSERT INTO cache (collection, id, expiration, file_path) values (?, ?, ?, ?)",
                (self.collection_name, identifier, expire_datetime, str(file_path)),
            )

            # Se guarda la respuesta en cache
            with file_path.open("wb") as file:
                for response_content in response.iter_content(chunk_size=32):
                    file.write(response_content)

        # Se entrega la como archivo de lectura
        return open(file_path, "r")
