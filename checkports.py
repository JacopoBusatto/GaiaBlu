from geopy.geocoders import Nominatim
import pandas as pd
import time
import os
from modules.config import DATA_PATH, PORT_PATH
# === Configura i percorsi ===
ANAGRAFICA_FILE = os.path.join(DATA_PATH, "anagraficaporti.csv")

# === Carica la lista di porti da aggiornare ===
df_base = pd.read_csv(ANAGRAFICA_FILE)
# === Geocoder ===
geolocator = Nominatim(user_agent="port_locator")

# === Cerca coordinate per porti senza lat/lon ===
df_missing = df_base[df_base[['lat', 'lon']].isnull().any(axis=1)].copy()

for i, row in df_missing.iterrows():
    query = f"{row['nome']}, {row['localita']}, Italia"
    try:
        location = geolocator.geocode(query, timeout=10)
        if location:
            df_missing.at[i, 'lat'] = location.latitude
            df_missing.at[i, 'lon'] = location.longitude
            print(f"{row['nome']} → OK")
        else:
            print(f"{row['nome']} → NOT FOUND")
    except Exception as e:
        print(f"{row['nome']} → ERROR: {e}")
    time.sleep(1)

# === Tieni solo i porti trovati ===
df_found = df_missing[df_missing[['nome', 'lat', 'lon']].notnull()][['nome', 'lat', 'lon']].copy()
# === Tieni i porti già completi ===
df_ok = df_base[df_base[['nome', 'lat', 'lon']].notnull()][['nome', 'lat', 'lon']].copy()

df_found = pd.concat([df_ok, df_found], ignore_index=True)


# === Aggiungi al file completo solo se non esiste già ===
if os.path.exists(PORT_PATH):
    df_existing = pd.read_csv(PORT_PATH)
    # Escludi quelli già presenti
    nuovi_nomi = ~df_found["nome"].isin(df_existing["nome"])
    df_to_add = df_found[nuovi_nomi]
    df_final = pd.concat([df_existing, df_to_add], ignore_index=True)
    print(f"Aggiunti {len(df_to_add)} porti nuovi.")
else:
    df_final = df_found
    print("Creato nuovo file con porti trovati.")

# === Salva ===
df_final[["nome", "lat", "lon"]].to_csv(PORT_PATH, index=False)
print(f"File aggiornato salvato in {PORT_PATH} ({len(df_final)} porti totali).")

