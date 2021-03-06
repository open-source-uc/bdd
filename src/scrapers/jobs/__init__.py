import logging
import sys
from time import time

SCRIPT_LOG = "script"
log = logging.getLogger(SCRIPT_LOG)


def initialize_log():
    formatter = logging.Formatter("%(asctime)s (%(filename)s) %(levelname)s: %(message)s")

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    script_err_handler = logging.FileHandler(filename=f"log/script_err_{int(time())}.log")
    script_err_handler.setFormatter(formatter)
    script_err_handler.setLevel(logging.ERROR)

    log.setLevel(logging.INFO)
    log.addHandler(console_handler)
    log.addHandler(script_err_handler)
