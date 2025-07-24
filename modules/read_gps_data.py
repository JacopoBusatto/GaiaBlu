from open_read_gps import open_port, close_port
from modules.config import INITIAL_SLEEP, MAX_TRIES_GPS, TRY_DELAY
from datetime import datetime
import time

def nmea_to_decimal(degrees_minutes, direction):
    if not degrees_minutes or direction not in "NSEW":
        return None
    try:
        deg = int(degrees_minutes[:2 if direction in "NS" else 3])
        min = float(degrees_minutes[2 if direction in "NS" else 3:])
        decimal = deg + min / 60
        if direction in "SW":
            decimal *= -1
        return decimal
    except:
        return None

def parse_gprmc_line(line):
    try:
        if not line.startswith("$GPRMC"):
            return {}
        fields = line.split(",")
        if len(fields) < 10 or fields[2] != "A":
            return {}

        lat = nmea_to_decimal(fields[3], fields[4])
        lon = nmea_to_decimal(fields[5], fields[6])

        # Orario (hhmmss) + Data (ddmmyy)
        time_str = fields[1]
        date_str = fields[9]

        if time_str and date_str:
            time_str_clean = time_str.split(".")[0]
            dt = datetime.strptime(date_str + time_str_clean, "%d%m%y%H%M%S")
        else:
            dt = None

        return {
            "LAT": round(lat, 6),
            "LON": round(lon, 6),
            "GPS_TIME": dt.isoformat() if dt else "NaT"
        }
    except Exception as e:
        print(f"[gps] Errore parsing: {e}")
        return {}

def get_gps_data():
    port = open_port()
    try:
        time.sleep(INITIAL_SLEEP)
        for _ in range(MAX_TRIES_GPS):
            raw = port.readline().decode("utf-8").strip()
            result = parse_gprmc_line(raw)

            if result:
                return result

            time.sleep(TRY_DELAY)

        # solo se dopo max_tries non troviamo nulla
        print("[gps] Nessuna riga $GPRMC valida trovata.")
        return {}
    except Exception as e:
        print(f"[gps] Errore lettura: {e}")
        return {}
    finally:
        close_port(port)

