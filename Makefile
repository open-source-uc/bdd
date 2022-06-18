all: requirements.txt

requirements.txt: poetry.lock
	poetry export -f requirements.txt -o requirements.txt


# TODO: simplificar esto

.PHONY: prod
prod: requirements.txt
	docker-compose \
		--project-name bdd-uc-prod \
		-f docker-compose.yml \
		-f dockerfiles/docker-compose.prod.yml \
		up --build

.PHONY: dev
dev: requirements.txt
	docker-compose \
		--project-name bdd-uc-dev \
		-f docker-compose.yml \
		-f dockerfiles/docker-compose.dev.yml \
		up --build
