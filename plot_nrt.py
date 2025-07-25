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

def get_last_valid_row(file_path):
    with open(file_path, "r") as f:
        lines = [line for line in f if not line.startswith("/")]
    if len(lines) < 2:
        return None
    header = lines[0].strip().split(",")
    last_row = lines[-1].strip().split(",")
    return pd.Series(dict(zip(header, last_row)))

def update_time_series(ax, times, c443, a441, start_time, filter_on, filter_off, end_time):
    ax.clear()
    ax.plot(times, c443, label="C443.7", color="blue")
    ax.plot(times, a441, label="A441.6", color="red")

    ax.set_title("Serie temporale C443.7 / A441.6")
    ax.set_xlabel("UTC")
    ax.set_ylabel("coeff. [1/m]", labelpad=10)
    ax.grid(True)
    ax.legend()

    ax.set_xlim(start_time, end_time)
    ax.axvspan(filter_on, filter_off, color="#dddddd", alpha=0.5, zorder=0)

    xticks = [start_time, filter_on, filter_off, end_time]
    ax.set_xticks(xticks)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

def update_flux_series(ax, times, flowin, flowout, start_time, end_time, filter_on=None, filter_off=None):
    ax.clear()
    ax.plot(times, flowin, label="FLOWIN", color="green")
    ax.plot(times, flowout, label="FLOWOUT", color="orange")

    ax.set_title("Serie temporale flusso (L/min)")
    ax.set_xlabel("UTC")
    ax.set_ylabel("Flusso [L/min]", labelpad=10)
    ax.grid(True)
    ax.legend()

    ax.set_xlim(start_time, end_time)

    if filter_on and filter_off:
        ax.axvspan(filter_on, filter_off, color="#dddddd", alpha=0.5, zorder=0)
        ax.set_xticks([start_time, filter_on, filter_off, end_time])  # ← match con ACS
    else:
        ax.set_xticks([start_time, end_time])  # fallback minimale

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

def update_spectra(ax, row):
    def parse_lambda_keys(df_columns, prefix):
        return sorted(
            [(float(col.split("_")[1]), col) for col in df_columns if col.startswith(prefix)],
            key=lambda x: x[0]
        )

    a_keys = parse_lambda_keys(row.index, "A_")
    c_keys = parse_lambda_keys(row.index, "C_")

    try:
        lambda_a, a_vals = zip(*[(l, float(row[k])) for l, k in a_keys])
        lambda_c, c_vals = zip(*[(l, float(row[k])) for l, k in c_keys])
    except ValueError:
        return

    ax.clear()

    tot_dis = int(float(row.get("TOT_DIS", 0)))
    ax.set_facecolor("#eeeeee" if tot_dis == 1 else "white")

    ax.plot(lambda_a, a_vals, label="A(λ)", color="red")
    ax.plot(lambda_c, c_vals, label="C(λ)", color="blue")

    ax.set_xlabel("λ [nm]")
    ax.set_ylabel("coeff. [1/m]", labelpad=10)
    ax.set_title(row.get("GPS_TIME", ""))
    ax.legend()
    ax.grid(True)

def plot_loop():
    existing_files = set(glob(os.path.join(OUT_PATH, FILE_PREFIX + "*" + FILE_SUFFIX)))

    while True:
        file_path = wait_for_new_file(existing_files)
        existing_files.add(file_path)
        time.sleep(5)

        print(f"[PLOT] Inizio monitoraggio di: {os.path.basename(file_path)}")
        last_mod_time = os.path.getmtime(file_path)
        last_mod_change_detected = time.time()

        plt.ion()
        plt.rcParams['toolbar'] = 'none'
        plt.close("all")
        fig, axs = plt.subplots(2, 2, figsize=(14, 7))
        fig.canvas.manager.set_window_title("Visualizzazione ACS")
        fig.subplots_adjust(wspace=0.3, hspace=0.4)
        fig.delaxes(axs[0][1])  # lasciamo solo in alto a sinistra, in basso a sinistra e in basso a destra

        ax_time     = axs[0][0]
        ax_flux     = axs[1][0]
        ax_spectrum = axs[1][1]

        times, c443, a441 = [], [], []
        flowin_series, flowout_series = [], []
        inizializzato = False

        while True:
            if not os.path.exists(file_path):
                print("[AVVISO] Il file non esiste più.")
                break

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
                flowin_series.append(float(row.get("FLOWIN", "nan")))
                flowout_series.append(float(row.get("FLOWOUT", "nan")))

                if not inizializzato:
                    start_time_utc  = gps_time
                    filter_on_utc   = start_time_utc + timedelta(minutes=FILTER_ON_MINUTE)
                    filter_off_utc  = start_time_utc + timedelta(minutes=FILTER_OFF_MINUTE)
                    end_time_utc    = start_time_utc + timedelta(minutes=ACQUISITION_LENGTH)
                    inizializzato = True

                update_time_series(ax_time, times, c443, a441, start_time_utc, filter_on_utc, filter_off_utc, end_time_utc)
                update_flux_series(ax_flux, times, flowin_series, flowout_series, start_time_utc, end_time_utc, filter_on_utc, filter_off_utc)
                update_spectra(ax_spectrum, row)

                fig.tight_layout()
                plt.pause(0.5)

            except Exception as e:
                if isinstance(e, (KeyboardInterrupt, RuntimeError)):
                    break
                print(f"[ERRORE plot] {type(e).__name__}: {e}")
                time.sleep(REFRESH_INTERVAL_PLOT)

if __name__ == "__main__":
    try:
        plot_loop()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[PLOT] Errore inatteso: {type(e).__name__}: {e}")
