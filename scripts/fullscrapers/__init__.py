import logging
import sys

SCRIPT_LOG = "script"

formatter = logging.Formatter("%(asctime)s (%(filename)s) %(levelname)s: %(message)s")

console_handler = logging.StreamHandler(stream=sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

script_err_handler = logging.FileHandler(filename="log/script_err.log")
script_err_handler.setFormatter(formatter)
script_err_handler.setLevel(logging.ERROR)

log = logging.getLogger(SCRIPT_LOG)
log.setLevel(logging.INFO)
log.addHandler(console_handler)
log.addHandler(script_err_handler)
