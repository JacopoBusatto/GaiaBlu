from open_read_ts import open_port, close_port
from modules.config import INITIAL_SLEEP, MAX_TRIES, TRY_DELAY
import time
import re

def parse_ts_line(line):
    """Estrae TEMP1 (t1), TEMP2 (t2) e SAL (s) da una riga del termosalinometro."""
    try:
        match_t1 = re.search(r"t1=\s*([\d\.]+)", line)
        match_t2 = re.search(r"t2=\s*([\d\.]+)", line)
        match_sal = re.search(r"s=\s*([\d\.]+)", line)

        if match_t1 and match_t2 and match_sal:
            return {
                "TEMP1": float(match_t1.group(1)),
                "TEMP2": float(match_t2.group(1)),
                "SAL": float(match_sal.group(1)),
            }
    except Exception as e:
        print(f"[ts] Errore parsing: {e}")
    return {}

def get_ts_data():
    port = open_port()
    try:
        time.sleep(INITIAL_SLEEP)
        for _ in range(MAX_TRIES):
            raw = port.readline().decode("utf-8").strip()
            result = parse_ts_line(raw)
            if result:
                return result
            time.sleep(TRY_DELAY)
        print("[ts] Nessuna riga valida trovata.")
        return {}
    except Exception as e:
        print(f"[ts] Errore lettura: {e}")
        return {}
    finally:
        try:
            close_port(port)
        except:
            pass
