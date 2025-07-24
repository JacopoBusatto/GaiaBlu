import geopandas as gpd
from shapely.geometry import Point
from pyproj import Geod
from modules.config import COASTLINE_PATH
from modules.porti_mediterranei import PORTI_MEDITERRANEI
from geopy.distance import geodesic


# === Costanti ===
geod = Geod(ellps="WGS84")

# === Caricamento linea di costa ===
try:
    coastlines = gpd.read_file(COASTLINE_PATH)
except Exception as e:
    coastlines = None
    print(f"[DIST] Errore nel caricamento coastline: {e}")

def distanza_dalla_costa(lat, lon):
    """
    Calcola la distanza geodetica alla linea di costa piu vicina (in km).
    """
    if coastlines is None:
        return float("nan")

    p = Point(lon, lat)
    min_dist_km = float("inf")

    for geom in coastlines.geometry:
        if geom.is_empty:
            continue
        nearest = geom.interpolate(geom.project(p))
        _, _, dist_m = geod.inv(lon, lat, nearest.x, nearest.y)
        min_dist_km = min(min_dist_km, dist_m / 1000)
        min_dist_nm = min_dist_km / 1.852
    return round(min_dist_nm, 3)
