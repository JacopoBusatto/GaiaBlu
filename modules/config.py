# ============================ CONFIGURAZIONE ACQUISIZIONE DATI ============================

# Durata del ciclo di acquisizione (in minuti)
ACQUISITION_LENGTH = 15       # Tempo totale di ogni acquisizione
START_MINUTE       = 0        # Minuto dell’ora in cui inizia il ciclo (es. 0 per HH:00)
ACS_LATENCY        = 1        # Ritardo dopo accensione ACS prima dell'inizio reale

# ============================ CONTROLLO VALVOLA FILTRAZIONE ============================

# Minuti relativi all'inizio in cui accendere/spegnere la valvola filtro
FILTER_ON_MINUTE  = 5         # Attiva la valvola al minuto 5
FILTER_OFF_MINUTE = 10        # Disattiva la valvola al minuto 10

# Comandi da passare all’eseguibile per controllo valvola
FILTER_ON  = "-c:6 -r:1#1 >nul"   # Comando per attivare la valvola
FILTER_OFF = "-c:6 -r:1#0 >nul"   # Comando per disattivare la valvola

# Path eseguibile per controllo valvola (RELAY)
RELAY_PATH = "C:/Users/ridopoco/IOPs/USBRelay.exe"

# ============================ CONTROLLO PRESE DI CORRENTE (USB) ============================

# Path eseguibile per controllo prese (USB relay)
SOCKET_PATH = "C:/Users/ridopoco/USBRelay_libary/USBRelay_libary/TestApp/CommandApp_USBRelay.exe HURTM "

# ID delle prese associate agli strumenti
PRESA_ACS  = "01"     # Presa che controlla ACS
PRESA_FLUX = "02"     # Presa che controlla il flussimetro

# ============================ FILE E PATH ============================

# Cartelle di output e dati
OUT_PATH    = "C:/Users/ridopoco/GaiaBlu/acquisizioni/"    # Dove salvare i file di acquisizione
DATA_PATH   = "C:/Users/ridopoco/GaiaBlu/data/"            # Dove si trovano shapefile e porti

# File per coastlines e lista porti
COASTLINE_PATH = f"{DATA_PATH}gshhs.shp"       # Shapefile delle coste
PORT_PATH      = f"{DATA_PATH}lista_porti.csv" # Lista dei porti italiani

# Prefisso/suffisso usati per generare i nomi dei file di output
FILE_PREFIX = "output_"
FILE_SUFFIX = ".txt"

# ============================ GESTIONE PLOT E VISUALIZZAZIONE ============================

# Frequenza aggiornamento grafici in tempo reale (secondi)
REFRESH_INTERVAL_PLOT = 5

# ============================ GESTIONE LETTURA STRUMENTI ============================

# Numero massimo di tentativi per lettura strumenti
MAX_TRIES     = 7     # Tutti gli strumenti tranne GPS
MAX_TRIES_GPS = 7     # GPS ha gestione separata

# Delay tra un tentativo e l’altro (secondi)
TRY_DELAY = 0.05

# Ritardo iniziale dopo apertura della porta seriale
INITIAL_SLEEP = 0.05

# ============================ CONDIZIONE DI NAVIGAZIONE ============================

# Soglia di distanza minima (in miglia nautiche) dal porto più vicino per avviare acquisizione
SOGLIA_NM = 0.0  # 0.0 → sempre attivo; >0 → parte solo quando lontani da costa

# Frequenza con cui controllare la distanza dalla costa (secondi)
CHECK_INTERVAL = 60

