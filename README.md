## 🌊 GAIA BLU – Sistema di acquisizione automatica e controllo strumenti a bordo

**GAIA BLU** è un sistema modulare per l’acquisizione automatica di dati oceanografici da strumenti scientifici installati su nave. Il sistema:

- gestisce connessioni **seriali** a strumenti (GPS, ACS, flussimetro, termosalinometro);
- regola accensione/spegnimento strumenti via **prese USB controllabili** e **relay**;
- avvia e termina l’acquisizione in base alla **distanza dalla costa**;
- salva file di dati con header compatibile IDL e **visualizza** i dati in tempo reale;
- registra log **colorati** e su file rotanti per debugging e diagnostica.

---

## 📂 Struttura del progetto

### 1. ✨ Moduli principali

| Script | Funzione |
|--------|----------|
| `manager.py` | Controlla l’intero sistema: avvia `acquisition.py` e `plot_nrt.py` se la nave è lontana dalla costa. Spegne strumenti se troppo vicina. |
| `acquisition.py` | Legge dati da tutti gli strumenti, regola la valvola filtro e salva i dati su file con header IDL. |
| `plot_nrt.py` | Visualizza in tempo reale: <br> - serie temporali (C443.7, A441.6) <br> - spettri ACS (A(lambda), C(lambda)) |

### 2. 🛂 Lettura strumenti (in `open_read_*.py`)

| Modulo | Strumento | Porta default |
|--------|-----------|---------------|
| `gps`   | GPS                 | COM5 |
| `ts`    | Termosalinometro    | COM9 |
| `flux`  | Flussimetro         | COM8 |
| `acs`   | ACS                 | COM7 |
| `lanmux`| LANMUX              | COM12 |
| `ac9`   | ACS legacy (AC-9)   | COM7 |  ❌ **(non utilizzato)**

Moduli **non utilizzati attivamente**: `open_read_ac9.py`, `open_read_lanmux.py`

Ogni modulo fornisce `open_port()`, `read_data()`, `close_port()`.

### 3. 🔍 Altri moduli

| Modulo | Funzione |
|--------|----------|
| `checkports.py` | Geocodifica lat/lon dei porti mancanti usando OpenStreetMap (Nominatim) |
| `logger_utils.py` | Log colorati su console **e** rotazione automatica su file (`flowthrough.log`) |
| `writer.py` | Scrive file output con intestazione IDL e dati da tutti gli strumenti |
| `read_*_data.py` | Wrapper per parsing dei dati letti da ciascun strumento |
| `config.py` | Parametri configurabili del sistema |
| `distance_to_nearest_port.py` | Calcola distanza in NM dal porto più vicino (usato da `manager.py`) |

---

## ⚙️ Requisiti

### 📉 Pacchetti Python

```bash
mamba install pandas matplotlib numpy pyserial colorama geopy
```

### 🔧 Librerie speciali

- [`pyACS`](https://github.com/) per parsing file `.dev` da ACS
- `USBRelay.exe` e `CommandApp_USBRelay.exe` per gestione prese
- File `.dev` calibrati per ogni ACS specifico (es. `ACS426.dev`)

---

## ▶️ Uso

```bash
python manager.py  # avvio automatico completo
```

oppure, in modalità debug:

```bash
python acquisition.py
python plot_nrt.py
```

---

## 🗒️ Esempio file di output

```
/begin_header
...
/end_header@
DATE,TIME,GPS_TIME,LAT,LON,FLOWIN,FLOWOUT,...
```

---

## 🚢 Contesto operativo

Progetto operativo a bordo della **nave da ricerca GAIA BLU** (CNR-ISMAR), per acquisizione continua e validazione live di dati bio-ottici, fisici e GPS.

---

## 🛎️ Contatti

> simone.colella@artov.ismar.cnr.it  
> gianluca.volpe@artov.ismar.cnr.it  
> jacopo.busatto@artov.ismar.cnr.it
