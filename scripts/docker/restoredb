#!/bin/sh

Help() {
    echo "Load a .dump file into the database"
    echo "Usage: $0 [-p (production)] [-h (help)] <dumpfile>"
}

dk_env=dev
dumpfile=0

while getopts hpf: option; do
    case $option in
        h) Help; exit;;
        p) dk_env=prod;;
        f) dumpfile="$OPTARG";;
   esac
done

if [[ -z $dumpfile ]]; then
    Help; exit 1
fi

docker exec -i \
    bdd-uc-${dk_env}_postgres_1 pg_restore \
    -U user -d database --clean --no-owner < "$dumpfile"
