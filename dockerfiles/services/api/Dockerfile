# La diferencia de desarrollo y producción es simplemente
# la opción de reloading, que se puede dejar en docker-compose

FROM python:3.9
WORKDIR /workspace

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY readme.md .
COPY src/ src/
