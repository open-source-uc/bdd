#!/bin/sh

Help() {
    echo "Create a .dump file of the full database"
    echo "Usage: $0 [-p (production)] [-h (help)]"
}

dk_env=dev

while getopts hp option; do
    case $option in
        h) Help; exit;;
        p) dk_env=prod;;
   esac
done

docker exec -i \
    bdd-uc-${dk_env}_postgres_1 pg_dump \
    -U user -Fc database > backup-$(date +%Y-%m-%d-%H%M%S).dump
