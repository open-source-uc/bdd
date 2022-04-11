all: requirements.txt

requirements.txt:
	poetry export -f requirements.txt -o requirements.txt


# TODO: simplificar esto

.PHONY: prod
prod: requirements.txt
	docker-compose \
		-f docker-compose.yml \
		-f dockerfiles/docker-compose.prod.yml \
		up --build

.PHONY: dev
dev: requirements.txt
	docker-compose \
		-f docker-compose.yml \
		-f dockerfiles/docker-compose.dev.yml \
		up --build
