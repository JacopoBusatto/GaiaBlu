import pandas as pd
from geopy.distance import geodesic
from modules.config import PORT_PATH

def distanza_dal_porto(lat, lon):
    try:
        df_porti = pd.read_csv(PORT_PATH)
    except Exception as e:
        print(f"[ERRORE] Impossibile leggere il file dei porti: {e}")
        return None, None

    min_dist = float("inf")
    porto_vicino = None

    for _, row in df_porti.iterrows():
        try:
            porto_coord = (float(row["lat"]), float(row["lon"]))
            dist_km = geodesic((lat, lon), porto_coord).km
            dist_nm = dist_km / 1.852
            if dist_nm < min_dist:
                min_dist = dist_nm
                porto_vicino = row["nome"]
        except:
            continue

    return porto_vicino, round(min_dist, 2) if porto_vicino else (None, None)
