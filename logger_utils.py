import sys
import os
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from colorama import init
from modules.config import LOG_PATH

init()
if os.name == 'nt':
    import colorama
    colorama.just_fix_windows_console()

# === ANSI colori per terminale ===
COLORS = {
    "manager": "\033[94m",      # blu
    "acquisition": "\033[92m",  # verde
    "plot": "\033[93m",         # giallo
    "error": "\033[91m",        # rosso
    "reset": "\033[0m"
}

os.makedirs(LOG_PATH, exist_ok=True)
LOG_FILE = os.path.join(LOG_PATH, "flowthrough.log")

file_logger = logging.getLogger("filelog")
file_logger.setLevel(logging.INFO)
file_handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(name)s] %(message)s'))
file_logger.addHandler(file_handler)

def log(source, message, error=False):
    timestamp = datetime.utcnow().isoformat(timespec="seconds")
    color = COLORS["error"] if error else COLORS.get(source, "")
    reset = COLORS["reset"]
    formatted = f"[{timestamp}] [{source.upper()}] {message}"
    print(f"{color}{formatted}{reset}", file=sys.stderr if error else sys.stdout)
    # Scrive sul file di log rotante
    sublogger = file_logger.getChild(source)
    if error:
        sublogger.error(message)
    else:
        sublogger.info(message)
