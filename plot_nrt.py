import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timezone, timedelta
import time
import os
from glob import glob
import ctypes
from modules.config import (
    OUT_PATH, FILE_PREFIX, FILE_SUFFIX, REFRESH_INTERVAL_PLOT, START_MINUTE,
    FILTER_ON_MINUTE, FILTER_OFF_MINUTE, ACQUISITION_LENGTH
)

STAGNANT_SECONDS = 15

def parse_lambda_keys(df_columns, prefix):
    return sorted(
        [(float(col.split("_")[1]), col) for col in df_columns if col.startswith(prefix)],
        key=lambda x: x[0]
    )

def get_last_valid_row(file_path):
    with open(file_path, "r") as f:
        lines = [line for line in f if not line.startswith("/")]
    if len(lines) < 2:
        return None
    header = lines[0].strip().split(",")
    last_row = lines[-1].strip().split(",")
    return pd.Series(dict(zip(header, last_row)))

def wait_for_new_file(existing_files):
    print("[ATTESA] In attesa di un nuovo file...")
    while True:
        current_files = set(glob(os.path.join(OUT_PATH, FILE_PREFIX + "*" + FILE_SUFFIX)))
        new_files = current_files - existing_files
        if new_files:
            new_file = sorted(list(new_files))[-1]
            print(f"[NUOVO FILE] Trovato: {os.path.basename(new_file)}")
            return new_file
        time.sleep(2)

def get_screen_resolution():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)  # width, height

def setup_figure():
    plt.ion()
    fig, axs = plt.subplots(2, 2, figsize=(12, 6))  # griglia 2x2
    plt.rcParams['toolbar'] = 'none'
    fig.canvas.manager.set_window_title("Visualizzazione ACS")
    fig.subplots_adjust(wspace=0.3, hspace=0.3)

    # Disattiva i subplot non usati
    fig.delaxes(axs[0][1])  # in alto a destra
    fig.delaxes(axs[1][0])  # in basso a sinistra

    ax_time = axs[0][0]     # in alto a sinistra
    ax_spectrum = axs[1][1] # in basso a destra

    return fig, ax_time, ax_spectrum


def plot_loop():
    existing_files = set(glob(os.path.join(OUT_PATH, FILE_PREFIX + "*" + FILE_SUFFIX)))

    while True:
        file_path = wait_for_new_file(existing_files)
        existing_files.add(file_path)
        time.sleep(5)  # attesa iniziale dopo creazione file

        print(f"[PLOT] Inizio monitoraggio di: {os.path.basename(file_path)}")
        last_mod_time = os.path.getmtime(file_path)
        last_mod_change_detected = time.time()

        # === Finestra a tutto schermo ===
        plt.ion()
        plt.rcParams['toolbar'] = 'none'
        fig, axs = plt.subplots(2, 2, figsize=(14, 7))
        fig.canvas.manager.set_window_title("Visualizzazione ACS")
        fig.subplots_adjust(wspace=0.3, hspace=0.4)
        fig.delaxes(axs[0][1])
        fig.delaxes(axs[1][0])

        ax_time = axs[0][0]
        ax_spectrum = axs[1][1]

        # === Dati accumulati ===
        times = []
        c443 = []
        a441 = []

        # === Setup temporale da primo record
        inizializzato = False

        while True:
            if not os.path.exists(file_path):
                print("[AVVISO] Il file non esiste più.")
                break

            # === Timeout se file non cresce ===
            current_mod_time = os.path.getmtime(file_path)
            if current_mod_time != last_mod_time:
                last_mod_time = current_mod_time
                last_mod_change_detected = time.time()
            elif time.time() - last_mod_change_detected >= STAGNANT_SECONDS:
                print(f"[ATTESA] File stagnante da {STAGNANT_SECONDS}s. Torno in attesa di nuovo file.")
                break

            row = get_last_valid_row(file_path)
            if row is None:
                time.sleep(REFRESH_INTERVAL_PLOT)
                continue

            try:
                gps_time = pd.to_datetime(row["GPS_TIME"])
                times.append(gps_time)
                c443.append(float(row.get("C_443.7", "nan")))
                a441.append(float(row.get("A_441.6", "nan")))

                # === Inizializza solo alla prima riga valida
                if not inizializzato:
                    start_time_utc  = gps_time
                    filter_on_utc   = start_time_utc + timedelta(minutes=FILTER_ON_MINUTE)
                    filter_off_utc  = start_time_utc + timedelta(minutes=FILTER_OFF_MINUTE)
                    end_time_utc    = start_time_utc + timedelta(minutes=ACQUISITION_LENGTH)
                    xticks = [start_time_utc, filter_on_utc, filter_off_utc, end_time_utc]
                    inizializzato = True

                # === Serie temporale ===
                ax_time.clear()
                ax_time.plot(times, c443, label="C443.7", color="blue")
                ax_time.plot(times, a441, label="A441.6", color="red")
                ax_time.set_title("Serie temporale C443.7 / A441.6")
                ax_time.set_xlabel("UTC")
                ax_time.set_ylabel("coeff. [1/m]", labelpad=10)
                ax_time.legend()
                ax_time.grid(True)

                ax_time.set_xlim(start_time_utc, end_time_utc)
                ax_time.axvspan(filter_on_utc, filter_off_utc, color="#dddddd", alpha=0.5, zorder=0)

                # Etichette con secondi
                ax_time.set_xticks(xticks)
                ax_time.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

                # === Spettri ===
                a_keys = parse_lambda_keys(row.index, "A_")
                c_keys = parse_lambda_keys(row.index, "C_")
                lambda_a, a_vals = zip(*[(l, float(row[k])) for l, k in a_keys])
                lambda_c, c_vals = zip(*[(l, float(row[k])) for l, k in c_keys])

                ax_spectrum.clear()
                tot_dis = int(float(row.get("TOT_DIS", 0)))
                ax_spectrum.set_facecolor("#eeeeee" if tot_dis == 1 else "white")
                ax_spectrum.plot(lambda_a, a_vals, label="A(λ)", color="red")
                ax_spectrum.plot(lambda_c, c_vals, label="C(λ)", color="blue")
                ax_spectrum.set_xlabel("λ [nm]")
                ax_spectrum.set_ylabel("coeff. [1/m]", labelpad=10)
                ax_spectrum.set_title(row["GPS_TIME"])
                ax_spectrum.legend()
                ax_spectrum.grid(True)

                fig.tight_layout()
                plt.pause(0.5)

            except Exception as e:
                if isinstance(e, (KeyboardInterrupt, RuntimeError)):
                    # Silenzia errori dovuti a chiusura forzata (es. da manager)
                    break
                print(f"[ERRORE plot] {type(e).__name__}: {e}")
                time.sleep(REFRESH_INTERVAL_PLOT)

if __name__ == "__main__":
    plot_loop()
