# logger_utils.py
import os
import sys
import logging
from datetime import datetime, timedelta
from colorama import init, Fore, Style
from modules.config import LOG_PATH, LOG_CLEANUP_ENABLED, LOG_RETENTION_DAYS

init()  # Abilita colori ANSI su Windows

# === Colori terminale ===
COLORS = {
    "manager": Fore.BLUE,
    "acquisition": Fore.GREEN,
    "plot": Fore.YELLOW,
    "error": Fore.RED,
    "reset": Style.RESET_ALL
}

# === Formatter console colorato ===
class ColorFormatter(logging.Formatter):
    def format(self, record):
        source = record.name
        color = COLORS.get(source, "")
        reset = COLORS["reset"]
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        return f"{color}[{timestamp}] [{source.upper()}] {record.getMessage()}{reset}"

# === Handler personalizzato che cambia file ogni giorno e cancella log vecchi ===
class DailyFileHandler(logging.Handler):
    def __init__(self, folder, base_filename="flowthrough", days_to_keep=None):
        super().__init__()
        self.folder = folder
        self.base_filename = base_filename
        self.days_to_keep = days_to_keep
        self.formatter = logging.Formatter("[%(asctime)s] [%(name)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
        self.current_date = None
        self.file = None
        self._rotate_if_needed()

    def _rotate_if_needed(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self.current_date:
            self.current_date = today
            if self.file:
                self.file.close()
            log_path = os.path.join(self.folder, f"{self.base_filename}_{today}.log")
            self.file = open(log_path, "a", encoding="utf-8")
            self._cleanup_old_logs()

    def _cleanup_old_logs(self):
        if self.days_to_keep is None:
            return  # pulizia disabilitata
        cutoff = datetime.now() - timedelta(days=self.days_to_keep)
        for fname in os.listdir(self.folder):
            if fname.startswith(self.base_filename) and fname.endswith(".log"):
                date_part = fname.replace(self.base_filename + "_", "").replace(".log", "")
                try:
                    file_date = datetime.strptime(date_part, "%Y-%m-%d")
                    if file_date < cutoff:
                        os.remove(os.path.join(self.folder, fname))
                except ValueError:
                    continue

    def emit(self, record):
        self._rotate_if_needed()
        msg = self.formatter.format(record)
        self.file.write(msg + "\n")
        self.file.flush()

    def close(self):
        if self.file:
            self.file.close()
        super().close()

# === Cache dei logger già creati ===
loggers = {}

def log(source: str, message: str):
    """
    Logger centralizzato per ogni componente (manager, acquisition, plot, ecc.)
    Ogni processo ha la sua cartella, e ogni giorno un nuovo file.
    """
    if source not in loggers:
        logger = logging.getLogger(source)
        logger.setLevel(logging.INFO)

        # Console handler colorato
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(ColorFormatter())
        logger.addHandler(ch)

        # File handler personalizzato
        folder = os.path.join(LOG_PATH, source)
        os.makedirs(folder, exist_ok=True)
        fh = DailyFileHandler(
            folder,
            base_filename="flowthrough",
            days_to_keep=LOG_RETENTION_DAYS if LOG_CLEANUP_ENABLED else None
        )
        logger.addHandler(fh)

        loggers[source] = logger

    loggers[source].info(message)
