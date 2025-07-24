from open_read_flux import open_port, close_port
from modules.config import INITIAL_SLEEP, MAX_TRIES, TRY_DELAY
import time

def parse_flux_line(linea):
    """Parsa una riga del flussimetro."""
    try:
        parts = linea.strip().split(",")
        if len(parts) >= 2:
            return {
                "FLOWIN": float(parts[0]),
                "FLOWOUT": float(parts[1]),
            }
    except Exception as e:
        print(f"[flux] Errore parsing: {e}")
    return {}

def get_flux_data():
    port = open_port()
    try:
        time.sleep(INITIAL_SLEEP)
        for _ in range(MAX_TRIES):
            raw = port.readline().decode("utf-8").strip()
            # print(f"[flux] Lettura grezza: {raw}")
            parsed = parse_flux_line(raw)
            if parsed:
                return parsed
            time.sleep(TRY_DELAY)  # attesa piccola prima di riprovare
        print("[flux] Nessun dato valido trovato")
        return {}
    except Exception as e:
        print(f"[flux] Errore lettura: {e}")
        return {}
    finally:
        close_port(port)
