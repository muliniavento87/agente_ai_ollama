from zoneinfo import ZoneInfo
import include.constants as c
import include.agente as a
import json
import datetime
import subprocess
import time
from pathlib import Path
import os
import shutil


C_INDEX = 99999999999 # 9
C_N_TRY = 99999999999 # 5

C_DIR_METADATI = Path("/workspace_metadati")
C_FILE_LOG = "LOOP_log.md"
C_FILE_CURRENT_PROMPT = "LOOP_prompt.md"
C_PATH_FILE_LOG = C_DIR_METADATI / C_FILE_LOG
C_PATH_FILE_CURRENT_PROMPT = C_DIR_METADATI / C_FILE_CURRENT_PROMPT


C_PROMPT_UTENTE = """
Crea una cartella "MINI_GAME" e creaci dentro un minigioco in html+js semplice ma graficamente ben curato.

Dentro la cartella crea:
- un repository dove committerai tutti gli interventi fino al termine lo sviluppo.
- un "README.md" per raccontare in massimo 200 parole, che gioco è e come si gioca (se non basta un doppio click per avviarlo spiega come avviarlo ed eventuali dipendenze).
- un file vuoto "TERMINATO_OK" (SOLO quando hai terminato tutto).

ATTENZIONE: quando hai terminato rispondi con "Sviluppo terminato".
"""

C_PROMPT_UTENTE = """
Crea una cartella "MINI_GAME_3D" e creaci dentro un minigioco in html+js semplice ma in 3D e graficamente ben curato.

Dentro la cartella crea:
- un repository dove committerai tutti gli interventi fino al termine lo sviluppo.
- un "README.md" per raccontare in massimo 200 parole, che gioco è e come si gioca (se non basta un doppio click per avviarlo spiega come avviarlo ed eventuali dipendenze).
- un file vuoto "TERMINATO_OK" (SOLO quando hai terminato tutto).

ATTENZIONE: quando hai terminato rispondi con "Sviluppo terminato".
"""

C_PROMPT_UTENTE = """
$C_PROMPT_UTENTE_CREA
CRITICO: $C_INIT_OR_RECOVER.

Dentro la cartella "MINI_GAME_3D_V2" crea:
- repository GIT (se non già presente) dove committerai tutti gli interventi fino al termine lo sviluppo.
- "README.md" per raccontare in massimo 200 parole, che gioco è, il genere, come si gioca e come si avvia (eventuali dipendenze da installare).

ATTENZIONE: al termine dello sviluppo fai dei test statici e verifica eventuali errori di sintassi. Quando hai finito rispondi con "Sviluppo terminato".
"""

C_PROMPT_UTENTE_CREA = """
Crea una cartella "MINI_GAME_3D_V2" e creaci dentro un minigioco in html+js semplice ma in 3D e graficamente molto ben curato.
Il genere del gioco 3D da sviluppare DEVE ESSERE "$C_GENERE_GIOCO".
"""

C_PROMPT_UTENTE_INIT = """Prima di tutto crea "CONTEXT.md" in "MINI_GAME_3D_V2", dove inserisci il genere del gioco e una brevissima idea di cosa vuoi sviluppare (fondamentali per riprendere lo sviluppo, se dovesse interrompersi bruscamente)"""

C_PROMPT_UTENTE_RECOVER = """Il tuo sviluppo si è interrotto bruscamente in corso d'opera. Prova a recuperare le informazioni da "CONTEXT.md" nella cartella "MINI_GAME_3D_V2" per continuare quello che stavi facendo."""

C_GENERI_GIOCHI = [
    "Endless Runner",
    "Platformer 3D (openspace, es. 'Super Mario 64')",
    "Puzzle / Fisica",
    "Turret / Dodge",
    "Mini Sports (es. 'Pong/Bowling/MicroGolf')",
    "Rhythm Lane (es. 'Guitar Hero')",
    "Idle / Clicker 3D",
    "Stealth / Evasione",
    "Micro Tower Defense",
    "Fishing / Catch",
    "First-Shooter",
    "Minicorsa con kart (es. 'Super Mario Kart')"
]

C_GENERI_GIOCHI = [
    "Mini Sports (mini-golf)",
    "Mini Sports (mini-soccer)",
    "Mini Sports (mini-basket)"
]

# -----------------------------------------
class FileManagement:
    @staticmethod
    def read_file(pf) -> str:
        try:
            with open(pf, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            Log.exc(e, "read_file(...)")

    @staticmethod
    def write_file(pf, content) -> None:
        try:
            with open(pf, "w", encoding="utf-8") as file:
                file.write(content)
        except Exception as e:
            Log.exc(e, "write_file(...)")
# -----------------------------------------
class Agente:
    V_SIMULAZIONE = False
    
    @staticmethod
    def run_pi(prompt, cartella="."):
        if Agente.V_SIMULAZIONE:
            secs = 4
            time.sleep(secs)
            return ""

        output = ""
        try:
            # log: crea file col prompt corrente (così puoi leggere l'ultimo avviato in "pi")
            FileManagement.write_file(str(C_PATH_FILE_CURRENT_PROMPT), prompt)
            comando = ["pi", "--no-session", "-p"]
            # Esegue il comando e cattura l'output
            with open(str(C_PATH_FILE_CURRENT_PROMPT), "r", encoding="utf-8") as f_in:
                output = subprocess.run(
                    comando,
                    stdin=f_in,
                    cwd=cartella,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
            output = output.stdout
            return output

        # ----- su subprocess.run(...) il messaggio di errore è in e.stderr -----
        except subprocess.CalledProcessError as e:
            # Se è crashato il server del modello dobbiamo riavviarlo
            # per triggerare il watcher che si ccupa di riavviarlo basta creare un file vuoto 'RUN_SERVER' dentro '.'
            if "model is not loaded" in str(e.stderr):
                with open("RUN_SERVER", "a", encoding="utf-8") as f:
                    f.write("\n")
                Log.exc(e, "Server modello crashato")
                
                secs = 120
                Log.msg("Attendo " + str(secs) + "s che il server riparta.")
                # attendo che il server riparta
                time.sleep(secs)
                Log.msg("Server avviato. Rilancio il prompt su Pi Agent")
                # rilancio il comando dopo aver fatto ripartire il server
                return Agente.run_pi(prompt, cartella)
            else:
                Log.exc(e, "run_pi() => subprocess.CalledProcessError")
                return ""
        except KeyboardInterrupt:
            # rilancio la stessa eccezione al chiamante padre
            raise
        except Exception as e:
            Log.exc(e, "run_pi() => Exception")
            return ""


# -----------------------------------------
class Log:
    V_INIT = "INIT"
    V_PROGRESS = "PROGRESS"
    V_DONE = "DONE"

    @staticmethod
    def log(t) -> str:
        print(f"{t}")
        # La modalità 'a' crea il file se non esiste, altrimenti aggiunge in fondo
        with open(str(C_PATH_FILE_LOG), "a", encoding="utf-8") as f:
            f.write(t+"\n")

    @staticmethod
    def time_print(stampa=True) -> str:
        try:
            # Imposta esplicitamente il fuso orario desiderato (es. Italia)
            ora = datetime.datetime.now(ZoneInfo("Europe/Rome")).strftime("%H:%M:%S")
            ts = f"[{ora}]"
            if stampa:
                Log.log(ts)
            return ts;
        except Exception as e:
            err = "[Eccezione] [time_print()] " + str(e)
            Log.log(err)

    @staticmethod
    def datetime_print(stampa=True) -> str:
        try:
            # Imposta esplicitamente il fuso orario desiderato (es. Italia)
            data_ora = datetime.datetime.now(ZoneInfo("Europe/Rome")).strftime("%Y-%m-%d %H:%M:%S")
            ts = f"[{data_ora}]"
            if stampa:
                Log.log(ts)
            return ts;
        except Exception as e:
            err = "[Eccezione] [datetime_print()] " + str(e)
            Log.log(err)

    @staticmethod
    def llm_model(t):
        ts = Log.time_print(False)
        Log.log(f"{ts} [LLM Model] {t}")
        Log.log("---------------------------")

    @staticmethod
    def msg(t):
        ts = Log.time_print(False)
        Log.log(f"{ts} [Msg] {t}")
        Log.log("---------------------------")
    
    @staticmethod
    def err(t):
        ts = Log.time_print(False)
        Log.log(f"{ts} [Errore] {t}")
        Log.log("---------------------------")
    
    @staticmethod
    def exc(e, t):
        ts = Log.time_print(False)
        Log.log("===========================")
        Log.log(f"{ts} [Eccezione] {t}")

        # Estrae tutti gli attributi pubblici e i loro valori in un dizionario
        dic = {
            attr: getattr(e, attr) 
            for attr in dir(e) 
            if not attr.startswith('_') and not callable(getattr(e, attr))
        }
        err = json.dumps(dic, indent=4, default=str)
        Log.log(err)
        Log.log("===========================")

# sposto cartelle
def process_workspaces():
    source_dir = "/workspace"
    dest_dir = "/workspace_metadati"

    # Verifica che la cartella di origine esista
    if not os.path.exists(source_dir):
        print(f"Errore: La cartella di origine '{source_dir}' non esiste.")
        return

    # Crea la cartella di destinazione se non esiste già
    os.makedirs(dest_dir, exist_ok=True)

    # Itera sugli elementi presenti in /workspace
    for entry in os.scandir(source_dir):
        # Filtriamo solo le directory (escludiamo eventuali file isolati)
        if entry.is_dir():
            old_path = entry.path
            original_name = entry.name

            # 1. Calcola il timestamp corrente (es. 20260606_153045)
            timestamp = datetime.datetime.now(ZoneInfo("Europe/Rome")).strftime("%Y%m%d_%H%M%S")

            # 2. Crea il nuovo nome e il percorso di destinazione
            new_name = f"{original_name}_{timestamp}"
            dest_path = os.path.join(dest_dir, new_name)

            try:
                # 3. Sposta e rinomina la cartella nella destinazione
                shutil.move(old_path, dest_path)
                print(f"[SUCCESSO] '{original_name}' -> rinominata in '{new_name}' e spostata.")
            except Exception as e:
                print(f"[ERRORE] Impossibile spostare '{original_name}': {e}")
                continue

            # 4. Aspetta un secondo prima della prossima iterazione
            time.sleep(1)

#
def recupera_genere_gioco():
    # 1. Recupera il timestamp attuale come numero intero positivo (secondi dall'epoca Unix)
    timestamp_attuale = int(time.time())
    # 2. Calcola il modulo 12 per ottenere un numero compreso tra 0 e 11
    indice = timestamp_attuale % len(C_GENERI_GIOCHI)
    Log.msg(f"recupera_genere_gioco => indice: {indice} => genere scelto: {C_GENERI_GIOCHI[indice]}")
    # 3. Recupera la voce del genere corrispondente all'indice
    genere_selezionato = C_GENERI_GIOCHI[indice]
    return genere_selezionato


if __name__ == "__main__":
    try:
        CARTELLA_LAVORO = "/workspace"
        C_PATH_FILE_LOG.touch(exist_ok=True)
        C_PATH_FILE_CURRENT_PROMPT.touch(exist_ok=True)

        index = 0
        index_try = 0
        while True:
            if index >= C_INDEX:
                Log.msg(f"Terminati i task [{index+1} di {C_INDEX}] => FINE")
                exit(0)
            else:
                Log.msg(f"Avvio task [task {index+1} di {C_INDEX}]")
                
            prompt_utente = C_PROMPT_UTENTE

            if index_try == 0:
                # sposto i progetti terminati
                process_workspaces()
                # nuovo
                c_genere_gioco = recupera_genere_gioco()
                prompt_utente = prompt_utente.replace("$C_PROMPT_UTENTE_CREA", C_PROMPT_UTENTE_CREA).replace("$C_GENERE_GIOCO", c_genere_gioco).replace("$C_INIT_OR_RECOVER", C_PROMPT_UTENTE_INIT)
            else:
                # recover
                prompt_utente = prompt_utente.replace("$C_PROMPT_UTENTE_CREA", "").replace("$C_INIT_OR_RECOVER", C_PROMPT_UTENTE_RECOVER)

            output = Agente.run_pi(prompt_utente, cartella=CARTELLA_LAVORO)
            if not output:
                # ko (nessun progresso)
                if index_try >= C_N_TRY:
                    Log.err(f"[task {index+1} di {C_INDEX}] => terminati i {C_N_TRY}  => ERRORE")
                    exit(1)
                Log.msg(f"[task {index+1} di {C_INDEX}] => NESSUN output ritento ancora [try {index_try+1} di {C_N_TRY}]")
                index_try = index_try + 1
                continue
            else:
                Log.msg(f"[task {index+1} di {C_INDEX}] => terminato OK , passo al prossimo!")
                index = index + 1
                index_try = 0

    except KeyboardInterrupt:
        Log.msg("\nInterruzione (CTRL+C): Chiusura del programma in corso...")
        exit(0)
    except Exception as e:
        Log.exc(e, "__main__ => Exception")
        exit(0)