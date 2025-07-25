import subprocess
import time
import os
import threading
from datetime import datetime
from modules.config import (
    OUT_PATH, FILE_PREFIX, FILE_SUFFIX,
    START_MINUTE, ACQUISITION_LENGTH, SOGLIA_NM,
    CHECK_INTERVAL, SOCKET_PATH, PRESA_ACS, PRESA_FLUX,
    RELAY_PATH, FILTER_OFF
)
from modules.distance_to_nearest_port import distanza_dal_porto
from modules.read_gps_data import get_gps_data
from logger_utils import log

def is_acquiring():
    now = datetime.utcnow()
    minute = now.minute
    fine = (START_MINUTE + ACQUISITION_LENGTH) % 60
    if START_MINUTE < fine:
        return START_MINUTE <= minute < fine
    else:
        return minute >= START_MINUTE or minute < fine

def get_last_output_file():
    files = [f for f in os.listdir(OUT_PATH) if f.startswith(FILE_PREFIX) and f.endswith(FILE_SUFFIX)]
    if not files:
        return None
    return os.path.join(OUT_PATH, sorted(files)[-1])

def estrai_gps_da_file(path):
    try:
        with open(path, "r") as f:
            lines = [l for l in f if not l.startswith("/")]
        if len(lines) < 2:
            return None
        last = lines[-1].strip().split(",")
        header = lines[0].strip().split(",")
        data = dict(zip(header, last))
        return float(data["LAT"]), float(data["LON"])
    except:
        return None

def start_acquisition():
    log("manager", "Avvio acquisition.py...")
    return subprocess.Popen(
        ["python", "-u", "acquisition.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def start_plot():
    log("manager", "Avvio plot_nrt.py...")
    return subprocess.Popen(
        ["python", "plot_nrt.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )

def stream_output(process, name):
    for line in process.stdout:
        log(name, line.strip(), error=False)

def stream_logs(process, name):
    for line in process.stderr:
        log(name, line.strip(), error=True)

def manager_loop():
    proc_acquisition = None
    proc_plot = None
    old_distance = None
    try:
        while True:
            # === Acquisizione posizione ===
            if is_acquiring():
                # log("manager", "Fase di acquisizione. Leggo da file output...")
                path = get_last_output_file()
                if not path:
                    log("manager", "Nessun file trovato.")
                    time.sleep(CHECK_INTERVAL)
                    continue
                pos = estrai_gps_da_file(path)
                if pos is None:
                    log("manager", "Riga non valida.")
                    time.sleep(CHECK_INTERVAL)
                    continue
                lat, lon = pos
            else:
                # log("manager", "Fase di attesa. Leggo da GPS...")
                gps = get_gps_data()
                lat, lon = gps.get("LAT"), gps.get("LON")

            if lat is None or lon is None:
                log("manager", "Coordinate non valide.")
                time.sleep(CHECK_INTERVAL)
                continue

            porto, distanza = distanza_dal_porto(lat, lon)
            if distanza < 2 * SOGLIA_NM:
                log("manager", f"Distanza da {porto}: {distanza} NM")

            if distanza < SOGLIA_NM:
                log("manager", f"Troppo vicino al porto di {porto}: {distanza} NM! Fermo acquisizione e spengo ACS!")
                if proc_acquisition and proc_acquisition.poll() is None:
                    proc_acquisition.terminate()
                    log("manager", "acquisition.py terminato.")
                    proc_acquisition = None
                if proc_plot and proc_plot.poll() is None:
                    proc_plot.terminate()
                    log("manager", "plot_nrt.py terminato.")
                    proc_plot = None
                # QUI SPENGO ACS e FLUX
                os.system(f"{SOCKET_PATH} close {PRESA_ACS}")
                os.system(f"{SOCKET_PATH} close {PRESA_FLUX}")

            elif distanza >= SOGLIA_NM:
                if (not proc_acquisition) or (proc_acquisition.poll() is not None):
                    if round(distanza,1) != old_distance:
                        log("manager", f"Distanza dal porto di {porto} adeguata: {distanza} NM")
                        log("manager",  "Accendo ACS e avvio acquisizione.")
                    os.system(f"{SOCKET_PATH} open {PRESA_FLUX}")
                    # os.system(f"{SOCKET_PATH} open {PRESA_ACS}")
                    time.sleep(2)
                    
                    proc_acquisition = start_acquisition()
                    threading.Thread(target=stream_output, args=(proc_acquisition, "acquisition"), daemon=True).start()
                    threading.Thread(target=stream_logs, args=(proc_acquisition, "acquisition"), daemon=True).start()

                if (not proc_plot) or (proc_plot.poll() is not None):
                    proc_plot = start_plot()
                    threading.Thread(target=stream_logs, args=(proc_plot, "plot"), daemon=True).start()
            old_distance = round(distanza,1)
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log("manager", "Interruzione manuale.")
        if proc_acquisition and proc_acquisition.poll() is None:
            proc_acquisition.terminate()
        if proc_plot and proc_plot.poll() is None:
            proc_plot.terminate()
        os.system(f"{RELAY_PATH} {FILTER_OFF}")
        time.sleep(10)
        os.system(f"{SOCKET_PATH} close {PRESA_ACS}")
        os.system(f"{SOCKET_PATH} close {PRESA_FLUX}")

if __name__ == "__main__":
    manager_loop()
