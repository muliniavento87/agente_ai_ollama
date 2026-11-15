import subprocess
import time
import include.utils as u
import include.constants as c

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
            u.FileManagement.write_file(c.C_CURRENT_PROMPT, prompt)
            comando = ["pi", "--no-session", "-p"]
            # Esegue il comando e cattura l'output
            with open(c.C_CURRENT_PROMPT, "r", encoding="utf-8") as f_in:
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
                u.Log.exc(e, "Server modello crashato")
                
                secs = 120
                u.Log.msg("Attendo " + str(secs) + "s che il server riparta.")
                # attendo che il server riparta
                time.sleep(secs)
                u.Log.msg("Server avviato. Rilancio il prompt su Pi Agent")
                # rilancio il comando dopo aver fatto ripartire il server
                return Agente.run_pi(prompt, cartella)
            else:
                u.Log.exc(e, "run_pi() => subprocess.CalledProcessError")
                return ""
        except KeyboardInterrupt:
            # rilancio la stessa eccezione al chiamante padre
            raise
        except Exception as e:
            u.Log.exc(e, "run_pi() => Exception")
            return ""
