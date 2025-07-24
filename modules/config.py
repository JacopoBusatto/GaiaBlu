# modules/config.py

# Delay iniziale dopo apertura porta
INITIAL_SLEEP = 0.05  # in secondi

# Tentativi di lettura massimi per ogni strumento
MAX_TRIES = 7
# Tentativi di lettura massimi per il GPS
MAX_TRIES_GPS = 7

# Ritardo tra un tentativo e l’altro di legttura dei sensori
TRY_DELAY = 0.05

# tempo di attesa tr accensione e avvio di acquisizione di acs
ACS_LATENCY = 1

# Durata del ciclo di acquisizione oraria (minuti)
ACQUISITION_LENGTH = 15

# Minuto dell'ora in cui inizia l'acquisizione (minuti)
START_MINUTE       = 00

# Minuto dallo start in cui viene attivata la valvola (minuti)
FILTER_ON_MINUTE   = 5

# Minuto dallo start in cui viene disattivata la valvola (minuti)
FILTER_OFF_MINUTE  = 10

# Path dell'eseguibile per controllo valvola
RELAY_PATH         = "C:/Users/ridopoco/IOPs/USBRelay.exe"
# Path dell'eseguibile che accende e spegne le prese
SOCKET_PATH     = "C:/Users/ridopoco/USBRelay_libary/USBRelay_libary/TestApp/CommandApp_USBRelay.exe HURTM "
PRESA_ACS          = "01"
PRESA_FLUX         = "02"

# Comando di attivazione valvola
FILTER_ON  = "-c:6 -r:1#1 >nul"

# Comando di disattivazione valvola
FILTER_OFF = "-c:6 -r:1#0 >nul"

# Cartella dove sono salvati gli output
# DATA_DIR = "C:/Users/ridopocoGaiaBlu/"
OUT_PATH = "C:/Users/ridopoco/GaiaBlu/acquisizioni/"

# File di coastlines e porti
DATA_PATH      = "C:/Users/ridopoco/GaiaBlu/data/"
COASTLINE_PATH = f"{DATA_PATH}gshhs.shp"
PORT_PATH      = f"{DATA_PATH}lista_porti.csv"

# Prefisso del file di output
FILE_PREFIX = "output_"

# Suffisso del file di output
FILE_SUFFIX = ".txt"

# tempo di aggiornamento plot (secondi)
REFRESH_INTERVAL_PLOT = 5

# Distanza minima dal porto piu vicino (miglia nautiche)
SOGLIA_NM = 1.0

# Frequenza di controllo della distanza minima (secondi)
CHECK_INTERVAL = 60
