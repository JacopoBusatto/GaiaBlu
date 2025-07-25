from geopy.geocoders import Nominatim
import pandas as pd
import time
import os
from modules.config import DATA_PATH, PORT_PATH
from colorama import init, Fore, Style
init(autoreset=True)

# === ANSI colori terminale (opzionale) ===
GREEN   = Fore.GREEN
YELLOW  = Fore.YELLOW
RED     = Fore.RED
CYAN    = Fore.CYAN
MAGENTA = Fore.MAGENTA
RESET   = Style.RESET_ALL

# === File input ===
ANAGRAFICA_FILE = os.path.join(DATA_PATH, "anagraficaporti.csv")

# === Carica file esistente (output) ===
if os.path.exists(PORT_PATH):
    df_output = pd.read_csv(PORT_PATH)
    print(f"{CYAN}File esistente caricato: {len(df_output)} porti presenti.{RESET}")
else:
    df_output = pd.DataFrame(columns=["nome", "lat", "lon"])
    print(f"{CYAN}Nessun file trovato, creato dataframe vuoto.{RESET}")

# === Carica nuovi porti da anagrafica ===
df_nuovi = pd.read_csv(ANAGRAFICA_FILE)

# === Normalizza nomi (spazi, casing) ===
df_output["nome"] = df_output["nome"].str.strip()
df_nuovi["nome"] = df_nuovi["nome"].str.strip()

# === Filtra solo porti non già presenti ===
df_non_presenti = df_nuovi[~df_nuovi["nome"].isin(df_output["nome"])].copy()
print(f"{CYAN}Nuovi porti da analizzare: {len(df_non_presenti)}{RESET}")

# === Dividi tra già completi e con lat/lon mancanti ===
df_completi = df_non_presenti[df_non_presenti[["lat", "lon"]].notnull().all(axis=1)][["nome", "lat", "lon"]]
df_mancanti = df_non_presenti[df_non_presenti[["lat", "lon"]].isnull().any(axis=1)]

# === Geocoder ===
geolocator = Nominatim(user_agent="port_locator")
porti_geocodificati = []
non_trovati = []

print(f"{CYAN}Cerco coordinate per {len(df_mancanti)} porti mancanti...{RESET}")
for i, row in df_mancanti.iterrows():
    query = f"{row['nome']}, {row['localita']}, Italia"
    try:
        location = geolocator.geocode(query, timeout=10)
        if location:
            print(f"{GREEN}{row['nome']} → OK{RESET}")
            porti_geocodificati.append({
                "nome": row["nome"],
                "lat": location.latitude,
                "lon": location.longitude
            })
        else:
            print(f"{MAGENTA}{row['nome']} → NOT FOUND{RESET}")
            non_trovati.append(row["nome"])
    except Exception as e:
        print(f"{RED}{row['nome']} → ERROR: {e}{RESET}")
        non_trovati.append(row["nome"])
    time.sleep(1)

# === Unisci tutti i porti da aggiungere ===
df_nuovi_porti = pd.concat([df_completi, pd.DataFrame(porti_geocodificati)], ignore_index=True)

# === Aggiungi al dataframe finale ===
df_output = pd.concat([df_output, df_nuovi_porti], ignore_index=True)

# === Ordina, rimuovi duplicati, salva ===
df_output = df_output.sort_values(by=["nome", "lat", "lon"], na_position="last")
df_output = df_output.drop_duplicates(subset="nome", keep="last")
df_output = df_output.sort_values("nome").reset_index(drop=True)
df_output.to_csv(PORT_PATH, index=False)

# === Report finale ===
print("\n🔍  === Riepilogo aggiornamento ===")
print(f"{CYAN}Porti già presenti:         {len(df_output) - len(df_nuovi_porti)}{RESET}")
print(f"{GREEN}Porti nuovi (completi):    {len(df_completi)}{RESET}")
print(f"{GREEN}Porti trovati online:      {len(porti_geocodificati)}{RESET}")
print(f"{MAGENTA}Porti NON trovati online: {len(non_trovati)}{RESET}")
print(f"{CYAN}Totale nel file finale:    {len(df_output)}{RESET}")
print(f"\n📁  File salvato in: {PORT_PATH}")
