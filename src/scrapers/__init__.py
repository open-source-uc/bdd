import os
from contextlib import asynccontextmanager

from aiohttp_client_cache.backends.sqlite import SQLiteBackend
from aiohttp_client_cache.session import CachedSession

from .buscacursos import get_available_terms, get_courses
from .catalogo import get_subjects


class RequestCachedSessions:
    "Clase auxiliar para utilizar sesiones asíncronas con cache"

    def __init__(self, cache_dir: str = ".cache") -> None:
        self._buscacursos = None
        self._catalogo = None

        self.__cache_buscacursos = SQLiteBackend(
            cache_name=os.path.join(cache_dir, "buscacursos.sql"),
            allowed_methods=("GET", "POST"),
        )
        self.__cache_catalogo = SQLiteBackend(
            cache_name=os.path.join(cache_dir, "catalogo.sql"),
            allowed_methods=("GET", "POST"),
        )

    @asynccontextmanager
    async def buscacursos(self):
        if not self._buscacursos:
            self._buscacursos = CachedSession(
                base_url="https://buscacursos.uc.cl/", cache=self.__cache_buscacursos
            )
        yield self._buscacursos
        await self._buscacursos.close()
        self._buscacursos = None

    @asynccontextmanager
    async def catalogo(self):
        if not self._catalogo:
            self._catalogo = CachedSession(
                base_url="https://catalogo.uc.cl/", cache=self.__cache_catalogo
            )
        yield self._catalogo
        await self._catalogo.close()
        self._catalogo = None


request = RequestCachedSessions()
