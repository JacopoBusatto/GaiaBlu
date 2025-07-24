import sys
from datetime import datetime
from colorama import init

init()  # <<< questa riga abilita i colori in Windows cmd / Miniforge

# Colori ANSI per terminale
COLORS = {
    "manager": "\033[94m",      # blu
    "acquisition": "\033[92m",  # verde
    "plot": "\033[93m",         # giallo
    "error": "\033[91m",        # rosso
    "reset": "\033[0m"
}

def log(source, message, error=False):
    timestamp = datetime.utcnow().isoformat(timespec="seconds")
    color = COLORS["error"] if error else COLORS.get(source, "")
    reset = COLORS["reset"]
    formatted = f"[{timestamp}] [{source.upper()}] {message}"
    print(f"{color}{formatted}{reset}", file=sys.stderr if error else sys.stdout)
