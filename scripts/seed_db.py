import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.getcwd())
load_dotenv()


import asyncio
from time import time

from fullscrapers import buscacursos, catalogo, initialize_log
from sqlmodel import Session

from src.db import create_db, engine

# Start script
initialize_log()
create_db()

with Session(engine) as session:
    init_time = time()

    if sys.argv[1] in ("buscacursos", "bc"):
        asyncio.run(buscacursos.get_full_buscacursos(session, int(sys.argv[2]), int(sys.argv[3])))

    elif sys.argv[1] == "catalogo":
        asyncio.run(catalogo.get_full_catalogo(session))

    print(f"Time elapsed: {(time() - init_time) / 60:1f} minutes")
