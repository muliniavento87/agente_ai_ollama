from zoneinfo import ZoneInfo
import include.constants as c
import include.agente as a
import json
import datetime
import subprocess
import time
import os
from pathlib import Path

C_INDEX = 99999999999 # 9
C_N_TRY = 99999999999 # 5
C_LOG_FILE = "metadati_loop/LOOP_log.md"
C_CURRENT_PROMPT = "metadati_loop/LOOP_prompt.md"

C_PROMPT_UTENTE = """
CRITICO: Se un tool specifico non appare nella lista iniziale, usa sempre codemode con searchTools() per cercarlo prima di dichiarare che non è disponibile. Ogni tool può essere eseguito SOLO una volta per sessione.

## Obiettivo
Esegui i passaggi seguenti in modo sequenziale e solo 1 volta per passaggio:
1. Chiama il tool "task_diario_non_terminato" e riceverai un risultato "X_1".
2. Bivio in base al valore di "X_1":
    - Se "X_1" è un array con almeno 2 elementi recupera il primo elemento che sarà "X_2_id" (stringa) e il secondo elemento che sarà "X_2_descr" (stringa).
    - Altrimenti se "X_1" è un array vuoto, scegli a piacere uno sviluppo, crea una descrizione DESCR sintetica di cosa farà (max 200 parole), chiama il tool "crea_task_diario" (con questa descrizione DESCR) e riceverai un risultato "X_2_id" (stringa).
3. Se "X_1" era un array con almeno 2 elementi, vuol dire che c'è uno sviluppo già esistente nella cartella "X_2_id", troverai nel "README.md" di quella cartella i dettagli per proseguire e "X_2_descr" sarà un breve riassunto dello scopo di quello sviluppo.

## Regole per nuovi sviluppi
Se devi creare un nuovo sviluppo:
1. Scegli qualcosa di molto semplice e banale ma esteticamente curato.
2. Realizzalo con una o entrambe le tecnologie "Python" e/o "NodeJS".
3. IMPORTANTE: Inizializza un repository GIT nella cartella "X_2_id" recuperata dai tools.
4. IMPORTANTE: Sviluppa solo ed esclusivamente nella cartella "X_2_id", crea dentro un "README.md" con l'obiettivo e i dettagli tecnici dello sviluppo.

## Regole generali
1. IMPORTANTE: Ogni intervento sul progetto deve essere seguito da un commit su GIT per registrare le modifiche.
2. IMPORTANTE: Quando hai terminato lo sviluppo chiama il tool "completa_task_diario" e rispondi all'utente.
"""


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
            FileManagement.write_file(C_CURRENT_PROMPT, prompt)
            comando = ["pi", "--no-session", "-p"]
            # Esegue il comando e cattura l'output
            with open(C_CURRENT_PROMPT, "r", encoding="utf-8") as f_in:
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
        with open(C_LOG_FILE, "a", encoding="utf-8") as f:
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



if __name__ == "__main__":
    try:
        os.makedirs("metadati_loop", exist_ok=True)
        if not os.path.exists(C_LOG_FILE):
            Path(C_LOG_FILE).write_text("", encoding="utf-8")
        if not os.path.exists(C_CURRENT_PROMPT):
            Path(C_CURRENT_PROMPT).write_text("", encoding="utf-8")

        index = 0
        index_try = 0
        while True:
            if index >= C_INDEX:
                Log.msg(f"Terminati i task [{index+1} di {C_INDEX}] => FINE")
                exit(0)
            else:
                Log.msg(f"Avvio task [task {index+1} di {C_INDEX}]")

            output = Agente.run_pi(C_PROMPT_UTENTE)
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

    except KeyboardInterrupt:
        Log.msg("\nInterruzione (CTRL+C): Chiusura del programma in corso...")
        exit(0)
    except Exception as e:
        Log.exc(e, "__main__ => Exception")
        exit(0)