FROM mcr.microsoft.com/vscode/devcontainers/python:3.9
WORKDIR /workspace

RUN pip install "poetry>=1,<2"
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt -o requirements.txt
RUN poetry install
