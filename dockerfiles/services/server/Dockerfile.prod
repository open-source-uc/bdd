# Hay que generar la documentación, que consiste en arhcivos estáticos
FROM python:3.9 AS doc-generator
WORKDIR /workspace

# Install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Build
COPY docs docs
COPY mkdocs.yml .
COPY .git .git
RUN mkdocs build -d docs-build

# Server
FROM nginx:1.21 as server
WORKDIR /workspace

# Static files
COPY --from=doc-generator /workspace/docs-build/ /var/www/
