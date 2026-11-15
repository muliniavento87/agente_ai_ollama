import datetime
import json
from zoneinfo import ZoneInfo
from pathlib import Path
import shutil
import include.constants as c


#
stato_n_fase = -1
stato_last_task_file_f_1 = ""

# -----------------------------------------
class Log:
    V_INIT = "INIT"
    V_PROGRESS = "PROGRESS"
    V_DONE = "DONE"

    @staticmethod
    def log(t) -> str:
        print(f"{t}")
        # La modalità 'a' crea il file se non esiste, altrimenti aggiunge in fondo
        with open(c.C_LOG_FILE, "a", encoding="utf-8") as f:
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
    
    @staticmethod
    def write_state_progress(fase, stato, parametri=[]):
        debug_write_state_progress = False
        # Creiamo un dizionario Python con i parametri passati alla funzione
        dati = {
            "fase": str(fase),
            "stato": str(stato),
            "parametri": parametri,
        }
        if debug_write_state_progress:
            Log.log("------ AGGIORNO STATO con ------")
            Log.log(json.dumps(dati, indent=4, ensure_ascii=False))
            Log.log("--------------------------------")
        # Scriviamo direttamente il dizionario come JSON formattato nel file
        with open(c.C_STATO_ELAB, "w", encoding="utf-8") as file:
            json.dump(dati, file, indent=4, ensure_ascii=False)

    def read_state_progress():
        try:
            # Apriamo il file in modalità lettura ('r')
            with open(c.C_STATO_ELAB, "r", encoding="utf-8") as file:
                # json.load legge il file e lo converte direttamente in un dizionario Python
                return json.load(file)
        except FileNotFoundError:
            # Gestione utile: se il file non esiste ancora (perché non è stato mai scritto),
            # restituiamo una struttura di default per evitare errori nel codice.
            return {
                "fase": "-1",
                "stato": "INIT",
                "parametri": [],
            }
        except Exception as e:
            Log.exc(e, "read_state_progress(...)")

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
    
    @staticmethod
    def backup_cartella(path_src_dir, path_dst_dir) -> None:
        Path(path_dst_dir).mkdir(parents=True, exist_ok=True)
        shutil.move(path_src_dir, path_dst_dir)
