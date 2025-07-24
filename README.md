## 🌊 GAIA BLU – Sistema di acquisizione automatica e controllo strumenti a bordo

**GAIA BLU** è un sistema modulare per l’acquisizione automatica di dati oceanografici da strumenti scientifici installati su nave. Il sistema:

- gestisce connessioni **seriali** a strumenti (GPS, ACS, flussimetro, termosalinometro);
- regola accensione/spegnimento strumenti via **prese USB controllabili** e **relay**;
- avvia e termina l’acquisizione in base alla **distanza dalla costa**;
- salva file di dati con header compatibile IDL e **visualizza** i dati in tempo reale;
- registra log **colorati** centralizzati per debugging e diagnostica.

---

## 📂 Struttura del progetto

### 1. ✨ Moduli principali

| Script | Funzione |
|--------|----------|
| `manager.py` | Controlla l’intero sistema: avvia `acquisition.py` e `plot_nrt.py` se la nave è lontana dalla costa. Spegne strumenti se troppo vicina. |
| `acquisition.py` | Legge dati da tutti gli strumenti, regola la valvola filtro e salva i dati su file con header IDL. |
| `plot_nrt.py` | Visualizza in tempo reale: <br> - serie temporali (C443.7, A441.6) <br> - spettri ACS (A(λ), C(λ)) |

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
| `logger_utils.py` | Log con colori per manager / plot / acquisition / errori |
| `writer.py` | Scrive file output con intestazione IDL e dati da tutti gli strumenti |
| `read_*_data.py` | Wrapper per parsing dei dati letti da ciascun strumento |
| `config.py` | Parametri configurabili del sistema (es. porta ACS, durata acquisizione, path) |
| `distance_to_nearest_port.py` | Calcola distanza in NM dal porto più vicino (usato da `manager.py`) |

---

## ⚙️ Requisiti

### 📉 Pacchetti Python

```bash
pip install pandas matplotlib numpy pyserial colorama geopy
```

### 🔧 Librerie speciali

- [`pyACS`](https://github.com/) per parsing file `.dev` da ACS
- `USBRelay.exe` e `CommandApp_USBRelay.exe` per gestione prese
- File `.dev` calibrati per ogni ACS specifico (es. `ACS426.dev`)

---

## ▶️ Uso

### 1. Avvio sistema completo

```bash
python manager.py
```

Esegue automaticamente:
- verifica distanza dalla costa;
- accensione prese;
- avvio acquisizione dati e plotting;
- spegnimento se troppo vicini a un porto.

### 2. Avvio manuale (debug)

```bash
python acquisition.py
python plot_nrt.py
```

### 3. Controllo porti (una tantum)

```bash
python checkports.py
```

---

## 🗒️ Esempio file di output

```txt
/begin_header 
/IOPs FlowThrough System onboard R/V Gaia Blu 
/DATE  = YYYYMMDD 
/TIME  = decimal hours [hh.decimals] 
/LAT   = degrees north [deg.decimals] 
/LON   = degrees east [deg.decimals] 
...
/end_header@
DATE,TIME,GPS_TIME,LAT,LON,FLOWIN,FLOWOUT,TEMP1,TEMP2,SAL,...
20250723,18.567,2025-07-23T18:34:00,41.9057,12.4956,1.23,1.20,23.5,25.1,38.2,...
```

---

## 🚢 Contesto operativo

Progetto operativo a bordo della **nave da ricerca GAIA BLU** (CNR-ISMAR). Il sistema consente:
- acquisizione continua senza supervisione;
- protezione strumenti in prossimità della costa;
- visualizzazione live per validazione a bordo.

---

## 🛎️ Contatti

> **Istituto di Scienze Marine - CNR**  
> simone.colella@artov.ismar.cnr.it  
> gianluca.volpe@artov.ismar.cnr.it  
> jacopo.busatto@artov.ismar.cnr.it

---

## ✏️ TODO

- [ ] Esportazione automatica in formato NetCDF
- [ ] Refactor: unificazione dei moduli `open_read_*` in una classe comune per strumenti seriali
- [ ] Rilevamento automatico porte COM
- [ ] Aggiunta interfaccia grafica leggera (es. Qt, Dash o Textual)
- [ ] Integrazione sincronizzazione oraria con GPS (`GPS_TIME` -> `system clock`)
- [ ] Logging anche su file `.log` oltre che terminale
- [ ] Backup automatico su USB o rete locale
- [ ] Test automatici per moduli di lettura e validazione dati
- [ ] Setup script (`install.sh`, `requirements.txt`, `README.md` Git-ready)
- [ ] Rimozione moduli legacy (`open_read_ac9.py`, `lanmux`) se non più necessari
- [ ] Opzione debug interattivo per `acquisition.py`
