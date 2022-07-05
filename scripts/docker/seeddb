#!/bin/sh

Help() {
    echo "Run a scraper job (buscacursos or catalogo)"
    echo "Usage: $0 [-p (production)] [-h (help)] <job-name> [...options]"
    echo "Job names:"
    echo "  catalogo"
    echo "  buscacursos / bc --> options <year> <semester>"
}

dk_env=dev

while getopts hp option; do
    case $option in
        h) Help; exit;;
        p) dk_env=prod;;
   esac
done

docker exec -i \
    bdd-uc-${dk_env}_api_1 python \
    scripts/seed_db.py $*
