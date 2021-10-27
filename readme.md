# BDDUC

**Base De Datos Unificada y Comunitaria 📚**

## SetUp

### Python

Se utiliza python `3.9` para el desarrollo.
Esta versión puede ser instalada con [pyenv][pyenv]:

```bash
pyenv install 3.9
pyenv local 3.9
```

Además se necesita tener instalado [poetry][poetry].
Se pueden instalar las dependencias con:

```bash
poetry install
```
[pyenv]: https://github.com/pyenv/pyenv#simple-python-version-management-pyenv
[poetry]: https://python-poetry.org/

### Base de Datos

Se necesita tener instalado [PostgreSQl][postgresql-download].
Además se necesita activar la extensión [PostGIS][postgis], que se
puede hacer con:

```psql
CREATE EXTENSION IF NOT EXISTS postgis;
```

[postgresql-download]: https://www.postgresql.org/download/
[postgis]: https://postgis.net/documentation/

## Variables de entorno

Hay que rellenar las variable de entorno locales en un archivo `.env`.
Se puede obtener el template con:

```bash
cp .env.template .template
```

## Correr el servidor

```bash
uvicorn src.api.main:app --reload
```

## Documentación

La documentación se encuentra en `docs` y puede ser generada
gracias a [mkdocs-material][mkdocs-material] con:

```bash
# de forma estática
mkdocs build -d docs-site
# servidor de desarrollo
mkdocs serve
```
[mkdocs-material]: https://squidfunk.github.io/mkdocs-material/

## Tests

```bash
python -m pytest
```
