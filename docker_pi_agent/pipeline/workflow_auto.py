from pathlib import Path
from zoneinfo import ZoneInfo
import include.prompts as p
import include.utils as u
import include.fasi as f
import include.git as g
import include.constants as c
import include.agente as a


C_PROMPT_UTENTE = """
Voglio creare un gioco in 3D sul browser con html, js e css.
Usa le tecnologie e le librerie che ritieni più opportune.
Ispirati a Super Mario 64 uscito anni fa per Nintendo 64 e crea un platform con quello stile.
Crea solo 3 livelli, si accede al primo da un menu, e quando si trova la stella e la si cattura passandoci sopra, si genera una piccola animazione e si passa al livello successivo.
Deve essere possibile muoversi in una area 3D con una telecamera che mantiene la distanza fissa in terza persona e lo segue nei movimenti ma che non ruota col personaggio, quindi se mi giro su me stesso la camera inquadra me senza ruotare, facendomi vedere front fianchi e back del personaggio.
Crea un pool di 3 tipi di nemici che mi inseguono lentamente in ogni livello (metti 8 in totale da questo pool), facilmente evitabili perchè lenti. Ogni nemico mi insegue costantemente ma colpisce molto lentamente, un colpo andato a segno porta un attesa per quel nemico nel colpirmi di nuovo (di 8 secondi) così ho il tempo si scappare.
Se muoio (vita di 3 punti, ogni colpo nemico, che colpisce solo se il nemico si avvicina troppo, mi ruba uno dei 3) fai una breve animazione e fammi rinascere sul posto dopo 4 secondi.
Addobba ogni livello con piattaforme (stile Super Mario), sulle quali posso saltare per raggiungere posti in alto a più altezze e in una di queste ci sarà la stella per finire il livello.
Cura lo stile grafico dei personaggi nemici e di quello usato dall'utente (un clone di Super Mario). Cura graficamente anche le ambientazioni che non devono essere troppo banali e troppo spoglie, arredale con elementi della natura, elementi artificiali come mura, capanne, staccionate, ecc. . Usa uno stile cartonato e non troppo realistico (in stile Super Mario 64). Tutti i modelli 3D e la mappa non devono essere high poly ma nemmeno lowpoly, bilancia la complessità del rendering per far andare il gioco fluido.
"""

C_PROMPT_UTENTE = """
Crea un semplice file html statico che mostra la scritta "ciao"
"""

C_PROMPT_UTENTE = """
Creami un'applicazione in react per frontend e nodejs per backend.
L'app servirà da agenda, permetterà di collegare una serie di "post-it" ad una giornata del calendario (realizzala esteticamente gradevole).
L'app avrà una topbar con al centro la <Data attuale in formato, esempio, 27 Ottobre 2026 - 14:38:03> (con data, ora, secondi che si aggiorna in realtime senza necessità che l'utente refreshi la pagina manualmente)
L'app apre con il workspace del giorno corrente e mostra un piano bianco con a sinistra un pulsante con icona "+" che permette di creare un "Post-it".
I post-it saranno graficamente dei quadrati su una riga orizzontale disposti nello spazio disponibile (ognuno avrà una dimensione fissa 300x200). La riga andrà a capo se non ha spazio in orizzontale (nessn overflow o scroll).

Sulla topbar tutto a sinistra (a sinistra del titolo/data) c'è un tasto per aprire il calendario con la vista del mese ma navigabile per andare in altri mesi o anni.
Il calendario avrà i giorni cliccabili che aprono quel workspace di quel giorno.

Ogni postit creato sarà cliccabile e al click aprirà una modale (sola lettura, che renderizza il testo interno in markdown). Sulla modale ci sarà in alto a sinistra un tasto icona "matita" per poter abilitare l'edit del testo. Durante l'edit la renderizzazione in markdown sarà sostituita da una text area per poter editare/inserire nuovo testo. Ogni variazione del testo viene salvata automativamente (senza necessità di un tasto salva, non è nemmeno necessario ricliccare sulla matita). Quando l'utente dovesse però ricliccare sulla matita si ritornerà alla visualizzazione markdown (no edit) per mostrare il testo.

Tutti gli interventi con creazione e modifica postit e informazioni interne verranno salvate dal backend sul database sqlite.
I postit saranno legati ad un giorno dell'anno quindi dovranno essere legati a quella giornata selezionata e cambiandola dovrà aggiornarsi il workspace con i task della nuova giornata scelta.
"""

# http://192.168.1.219:11434


if __name__ == "__main__":
    try:
        # Crea la cartella dei metadati se non esiste
        Path(c.C_PATH_DIR_METADATI).mkdir(parents=True, exist_ok=True)
        
        with open(c.C_LOG_FILE, "w", encoding="utf-8") as ff:
            ff.write("")

        n_try = 10
        index_try = 0
        while True:
            # recupero eventuali progressi
            current_state = u.Log.read_state_progress()
            st_fase = int(current_state["fase"])
            st_stato = current_state["stato"]
            st_parametri = current_state["parametri"]

            # -----------------------------------------
            if st_fase < 0 or (st_fase == 0 and st_stato == u.Log.V_PROGRESS):
                # ============== Fase 0 ==============
                # (prompt utente => documento tecnico)
                # ====================================
                retry = False
                if st_stato == u.Log.V_PROGRESS:
                    retry = True
                else:
                    file_path = Path(c.C_PATH_FILE_OUTPUT_FASE_0)
                    if file_path.is_file():
                        # rimozione vecchio file
                        file_path.unlink()
                esito = f.Fasi.fase_0(C_PROMPT_UTENTE, retry)
                # nessun progresso => retry (max 'n_try' volte)
                if esito == 1:
                    # ko (nessun progresso)
                    if index_try >= n_try:
                        u.Log.err(f"fase_0() => terminati i {n_try} try => ERRORE")
                        exit(1)
                    index_try = index_try + 1
                    u.Log.msg(f"fase_0() => ritento {index_try} di {n_try} tentativi...")
                    continue
                # qualche progresso => retry (non sprechiamo i progressi)
                if esito == 2:
                    index_try = 0
                    retry = True
                    u.Log.msg(f"fase_0() => sono stati fatti dei progressi, continuo a tentare...")
                    # salvo stato progressi
                    st_fase = 0
                    st_stato = u.Log.V_PROGRESS
                    u.Log.write_state_progress(st_fase, st_stato)
                    continue
                # tutto ok => prossima fase
                index_try = 0
                st_fase = 0
                st_stato = u.Log.V_PROGRESS
                # salvo stato progressi
                u.Log.write_state_progress(st_fase, st_stato)

                # recupera stringa tag tasks
                pr = p.C_FASE_1_HELPER.replace("$DOC_FASE_0", c.C_OUTPUT_FASE_0)
                u.Log.msg(f"fase_0() => Recupero i task dal documento '{c.C_OUTPUT_FASE_0}'")
                tag_tasks = a.Agente.run_pi(p.C_FASE_1_HELPER)
                if not tag_tasks:
                    u.Log.err(f"fase_0() => ERRORE, nessuna stringa di tags ricevuta")
                    break
                else:
                    u.Log.msg(f"fase_0() => Trovati i task: {tag_tasks}")
                st_stato = u.Log.V_DONE
                st_parametri = [tag_tasks]
                # salvo stato progressi
                u.Log.write_state_progress(st_fase, st_stato, st_parametri)
            else:
                u.Log.msg(f"fase_0() => già terminata")

            # -----------------------------------------
            if (st_fase == 0 and st_stato == u.Log.V_DONE) or (st_fase == 1 and st_stato == u.Log.V_PROGRESS):
                # ================ Fase 1 ====================
                # (documento tecnico => task da implementare)
                # ============================================
                retry = False
                # Crea la cartella di lavoro se non esiste
                Path(c.C_OUT_DIR_IMPL).mkdir(parents=True, exist_ok=True)
                # Crea la cartella dei task generati se non esiste
                Path(c.C_PATH_DIR_TASKS_GENERATI).mkdir(parents=True, exist_ok=True)
                # Crea la cartella dei metadati se non esiste
                Path(c.C_PATH_DIR_METADATI).mkdir(parents=True, exist_ok=True)

                # se non presente inizializza repository git
                g.Git.init(c.C_PATH_DIR_TASKS_GENERATI)

                if st_stato == u.Log.V_PROGRESS:
                    retry = True

                tag_tasks = ""
                if len(st_parametri) > 0:
                    tag_tasks = st_parametri[0]
                esito = f.Fasi.fase_1(retry, tag_tasks)
                # nessun progresso => retry (max 'n_try' volte)
                if esito == 1:
                    # ko (nessun progresso ritentiamo)
                    if index_try >= n_try:
                        u.Log.err(f"fase_1() => terminati i {n_try} try => ERRORE")
                        exit(1)
                    retry = True
                    index_try = index_try + 1
                    u.Log.msg(f"fase_1() => ritento {index_try} di {n_try} tentativi...")
                    continue
                # qualche progresso => retry (non sprechiamo i progressi)
                elif esito == 2:
                    index_try = 0
                    retry = True
                    u.Log.msg(f"fase_1() => sono stati fatti dei progressi, continuo a tentare...")
                    # salvo stato progressi
                    st_fase = 1
                    st_stato = u.Log.V_PROGRESS
                    u.Log.write_state_progress(st_fase, st_stato, st_parametri)
                    continue
                elif esito == 99:
                    # dobbiamo generare ancora altri microtask
                    index_try = 0
                    u.Log.msg(f"fase_1() => continuiamo con la generazione dei microtask...")
                    # salvo stato progressi
                    st_fase = 1
                    st_stato = u.Log.V_PROGRESS
                    u.Log.write_state_progress(st_fase, st_stato, st_parametri)
                    continue
                # tutto ok => prossima fase
                index_try = 0
                # salvo stato progressi
                st_fase = 1
                st_stato = u.Log.V_DONE
                u.Log.write_state_progress(st_fase, st_stato)
            else:
                u.Log.msg(f"fase_1() => già terminata")

            # -----------------------------------------
            if (st_fase == 1 and st_stato == u.Log.V_DONE) or (st_fase == 2 and st_stato == u.Log.V_PROGRESS):
                # ================ Fase 2 ====================
                # (task da implementare => implementazione)
                # ============================================
                retry = False
                # Crea la cartella di lavoro se non esiste
                Path(c.C_OUT_DIR_IMPL).mkdir(parents=True, exist_ok=True)
                # Crea la cartella dei task generati se non esiste
                Path(c.C_PATH_DIR_TASKS_GENERATI).mkdir(parents=True, exist_ok=True)
                # Crea la cartella dei metadati se non esiste
                Path(c.C_PATH_DIR_METADATI).mkdir(parents=True, exist_ok=True)

                # se non presente inizializza repository git
                g.Git.init(c.C_OUT_DIR_IMPL)

                u.Log.msg(f"fase_2() => INIZIO")

                # loop sui task da elaborare
                while True:
                    # recupero eventuali progressi
                    current_state = u.Log.read_state_progress()
                    st_fase = int(current_state["fase"])
                    st_stato = current_state["stato"]
                    st_parametri = current_state["parametri"]

                    esito = f.Fasi.fase_2(st_parametri)
                    # nessun progresso => retry (max 'n_try' volte)
                    if esito == 1:
                        # ko (nessun progresso ritentiamo)
                        if index_try >= n_try:
                            u.Log.err(f"fase_2() => terminati i {n_try} try => ERRORE, Fase 2 KO => Termino programma")
                            exit(1)
                        index_try = index_try + 1
                        u.Log.err(f"fase_2() => riprovo ancora con lo stesso task (tentativo {index_try} di {n_try} disponibili)")
                        continue
                    # qualche progresso => retry (non sprechiamo i progressi)
                    elif esito == 2:
                        index_try = 0
                        retry = True
                        u.Log.msg(f"fase_2() => sono stati fatti dei progressi, continuo a tentare...")
                        # salvo stato progressi
                        st_fase = 2
                        st_stato = u.Log.V_PROGRESS
                        # non aggiorno il file di stato perchè è già gestito in f.Fasi.fase_2(...)
                        #u.Log.write_state_progress(st_fase, st_stato)
                        continue
                    elif esito == 9:
                        # errore grave, nessun task da elaborare (interrompo tutto)
                        exit(1)
                        break
                    elif esito == 99:
                        # salvo stato progressi
                        st_fase = 2
                        st_stato = u.Log.V_PROGRESS
                        # task terminato => proseguo col prossimo
                        continue

                    # Tutti i task sono stati terminati => FINE
                    index_try = 0
                    # salvo stato progressi
                    st_fase = 2
                    st_stato = u.Log.V_DONE
                    # non aggiorno il file di stato perchè è già gestito in f.Fasi.fase_2(...)
                    #u.Log.write_state_progress(st_fase, st_stato)
                    u.Log.msg(f"fase_2() => già terminata")
                    exit(0)

            else:
                u.Log.msg(f"fase_1() => già terminata")
            exit(0)
    except KeyboardInterrupt:
        u.Log.msg("\nInterruzione (CTRL+C): Chiusura del programma in corso...")
        exit(0)
    except Exception as e:
        u.Log.exc(e, "__main__ => Exception")
        exit(0)
