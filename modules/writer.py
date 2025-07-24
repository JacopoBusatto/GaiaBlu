from datetime import datetime
from open_read_acs import open_port, close_port

# === Costruzione dinamica da .dev ===
try:
    _, dev = open_port()
    C_KEYS = [f"C_{lam:.1f}" for lam in dev.lambda_c]
    A_KEYS = [f"A_{lam:.1f}" for lam in dev.lambda_a]
    close_port(_)
except Exception as e:
    print(f"[writer] Errore nel caricamento dev ACS: {e}")
    C_KEYS = []
    A_KEYS = []

BASE_KEYS = [
    "DATE", "TIME", "GPS_TIME",
    "LAT", "LON",
    "FLOWIN", "FLOWOUT",
    "TEMP1", "TEMP2", "SAL"
]

CAMPI_ORDINATI = BASE_KEYS + C_KEYS + A_KEYS + ["INT_TEMP", "EXT_TEMP", "TOT_DIS"]

def scrivi_header(file_path):
    """Scrive l'intestazione del file di output (stile IDL)."""
    with open(file_path, "w") as f:
        f.write("/begin_header \n")
        f.write("/IOPs FlowThrough System onboard R/V Gaia Blu \n")
        f.write("/DATE  = YYYYMMDD \n")
        f.write("/TIME  = decimal hours [hh.decimals] \n")
        f.write("/LAT   = degrees north [deg.decimals] \n")
        f.write("/LON   = degrees east [deg.decimals] \n")
        f.write("/FLOWIN = intake seawater flow (L/min) \n")
        f.write("/FLOWOUT = outtake seawater flow (L/min) \n")
        f.write("/TEMP1 = Seawater temperature laboratory  (Celsius degrees) [from TS sensor] \n")
        f.write("/TEMP2 = Seawater temperature environment (Celsius degrees) [from TS sensor] \n")
        f.write("/SAL = Seawater salinity ACS intake (psu) \n")
        f.write("/C_???.? = Attenuation coefficient at lambda ???.?nm \n")
        f.write("/A_???.? = Absorption  coefficient at lambda ???.?nm \n")
        f.write("/INT_TEMP = ACs internal temperature (Celsius degrees) \n") 
        f.write("/EXT_TEMP = ACs external temperature (Celsius degrees) \n")
        f.write("/TOT_DIS = Flag for acquisition mode (0 = total, 1 = dissolved) \n")
        f.write("/end_header@\n")
        f.write(",".join(CAMPI_ORDINATI) + "\n")  # intestazione CSV

def appendi_riga(file_path, data_dict):
    """Appende una riga di dati al file di output."""
    # Aggiorna automaticamente DATE e TIME se non presenti
    now = datetime.utcnow()
    if "DATE" not in data_dict:
        data_dict["DATE"] = now.strftime("%Y%m%d")
    if "TIME" not in data_dict:
        data_dict["TIME"] = f"{now.hour + now.minute / 60 + now.second / 3600:.6f}"

    # Prepara i valori nella giusta sequenza
    valori = []
    for key in CAMPI_ORDINATI:
        valore = data_dict.get(key)
        if valore is None:
            valori.append("NaN")
        elif isinstance(valore, float):
            valori.append(f"{valore:.6f}")
        else:
            valori.append(str(valore))
    
    with open(file_path, "a") as f:
        f.write(",".join(valori) + "\n")
