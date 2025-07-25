import time
import os
from datetime import datetime, timezone
from modules.read_gps_data import get_gps_data
from modules.read_flux_data import get_flux_data
from modules.read_ts_data import get_ts_data
from modules.read_acs_data import get_acs_data
from modules.writer import scrivi_header, appendi_riga
from modules.config import (
    ACQUISITION_LENGTH, START_MINUTE, FILTER_ON_MINUTE,
    FILTER_OFF_MINUTE, RELAY_PATH, FILTER_ON, FILTER_OFF,
    OUT_PATH, FILE_PREFIX, FILE_SUFFIX, MAX_TRIES, TRY_DELAY,
    ACS_LATENCY, SOCKET_PATH, PRESA_ACS
    )
from logger_utils import log
from math import isnan

def ora_locale():
    return datetime.now().astimezone()

def aspetta_minuto_zero():
    target_minute = (START_MINUTE - ACS_LATENCY) % 60
    while True:
        now = ora_locale()
        if now.minute == target_minute:
            # log("acquisition", f" Raggiunto minuto di start anticipato per latenza ACS ({ACS_LATENCY} min).")
            return
        time.sleep(5)

def main():
    now = ora_locale()
    log("acquisition", f"[LOOP] In attesa del prossimo minuto {START_MINUTE:02d}")

    while True:
        aspetta_minuto_zero()
        
        flusso = None
        for i in range(MAX_TRIES):
            try:
                dati_flux = get_flux_data()
                flusso = dati_flux.get("FLOWIN")
                if flusso is not None and flusso > 0:
                    break  # uscita anticipata se il flusso e' valido
            except Exception as e:
                log("acquisition", f"[CHECK] Errore lettura flusso (tentativo {i+1}): {e}")
            time.sleep(TRY_DELAY)

        if flusso is None or flusso <= 0:
            log("acquisition", f"[CHECK] Flusso assente ({flusso}), acquisizione saltata.")
            time.sleep(120)
            continue

        os.system(f"{SOCKET_PATH} open {PRESA_ACS}")
        time.sleep(ACS_LATENCY * 60)
        
        
        # === Inizia nuova acquisizione ===
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file_output = f"{OUT_PATH}{FILE_PREFIX}{timestamp}{FILE_SUFFIX}"
        scrivi_header(file_output)
        
        now = ora_locale()
        log("acquisition", f"[START] Scrittura su {file_output}")

        start_time = time.time()
        filtro_on  = False
        filtro_off = False
        tot_dis = 0  # 0=valvola aperta (default)
        try:
            while time.time() - start_time < ACQUISITION_LENGTH * 60:
                record = {}
                elapsed = time.time() - start_time
                now = ora_locale()

                # === Trigger filtro ON al minuto 5
                if not filtro_on and elapsed >= FILTER_ON_MINUTE * 60:
                    os.system(f"{RELAY_PATH} {FILTER_ON}")
                    filtro_on = True
                    tot_dis = 1
                    log("acquisition", f"[RELAY] Valvola commutata --> FILTRO ON")


                # === Trigger filtro OFF al minuto 10
                if not filtro_off and elapsed >= FILTER_OFF_MINUTE * 60:
                    os.system(f"{RELAY_PATH} {FILTER_OFF}")
                    filtro_off = True
                    tot_dis = 0
                    log("acquisition", f"[RELAY] Valvola riportata alla posizione originale --> FILTRO OFF")

                # === ORDINE DEFINITO ===
                record.update(get_gps_data())    # 1. GPS
                record.update(get_flux_data())   # 2. Flussimetro
                record.update(get_ts_data())     # 3. Termosalinometro
                record.update(get_acs_data())    # 4. ACS

                # === Controllo: almeno un valore non valido?
                scarta = False
                for v in record.values():
                    if v is None or v == "" or v == "NaN":
                        scarta = True
                        break
                    if isinstance(v, float) and isnan(v):
                        scarta = True
                        break

                if not scarta:
                    record["TOT_DIS"] = tot_dis
                    appendi_riga(file_output, record)
                # else:
                #     print(f"[WARN] Riga scartata per presenza di NaN o valori nulli", flush=True)

                appendi_riga(file_output, record)

        except KeyboardInterrupt:
            os.system(f"{SOCKET_PATH} close {PRESA_ACS}")
            break
        
        os.system(f"{RELAY_PATH} {FILTER_OFF}")
        os.system(f"{SOCKET_PATH} close {PRESA_ACS}")
        
        print(f"[END] Acquisizione terminata. In attesa del prossimo ciclo al minuto {START_MINUTE:02d}.", flush = True)
        
if __name__ == "__main__":
    main()
