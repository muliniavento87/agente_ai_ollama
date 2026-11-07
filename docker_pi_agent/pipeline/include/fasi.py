import include.utils as u
import include.prompts as p
import include.git as g
import include.constants as c
import include.agente as a
from pathlib import Path
import shutil
import os
import re


def natural_sort_key(s):
  # Estrae la parte numerica convertendola in intero, il resto resta stringa
  return [
      int(text) if text.isdigit() else text.lower()
      for text in re.split(r'(\d+)', s)
  ]

class Fasi:

    # RICH_UTENTE_2_DOC_TECNICO
    @staticmethod
    def fase_0(prompt_utente, is_a_retry=False):
        output = ""
        try:
            # Crea la cartella di lavoro se non esiste
            Path(c.C_OUT_DIR_IMPL).mkdir(parents=True, exist_ok=True)

            u.Log.msg("fase_0() => INIZIO")
            prompt = p.C_FASE_0.replace("$OUTPUT_FASE_0", c.C_PATH_FILE_OUTPUT_FASE_0).replace("$INPUT_PROMPT_UTENTE", prompt_utente).replace("$FILES_CARTELLE_DA_IGNORARE", c.C_IGNORARE).replace("$DUBBI", "").replace("$C_OUT_DIR_IMPL", c.C_OUT_DIR_IMPL)
            if is_a_retry:
                prompt = prompt.replace("$FASE_0_RETRY", p.C_FASE_RETRY)
            else:
                prompt = prompt.replace("$FASE_0_RETRY", "")
            u.Log.msg(f"fase_0() => Genero il documento tecnico '{c.C_FILE_OUTPUT_FASE_0}' dal prompt utente")
            output = a.Agente.run_pi(prompt)
            if not output:
                u.Log.msg("fase_0() => ERRORE, nessun output")
                file_path = Path(c.C_PATH_FILE_OUTPUT_FASE_0)
                if file_path.is_file():
                    u.Log.msg("fase_0() => No output ma ha fatto progressi")
                    # l'esecuzione ha prodotto risultati
                    return 2
            else:
                shutil.move(c.C_PATH_FILE_OUTPUT_FASE_0, c.C_OUTPUT_FASE_0)
                u.Log.llm_model(output)
                u.Log.msg("fase_0() => FINE ok")
                return 0
        except KeyboardInterrupt:
            raise
        except Exception as e:
            u.Log.exc(e, "fase_0() => Exception")
        # errore
        return 1

    # DOC_TECNICO_2_TASKS
    @staticmethod
    def fase_1(is_a_retry=False, tag_tasks=""):
        max_task_alla_volta = 1
        list_tag_tasks = tag_tasks.split(',')
        n_list_tag_tasks = len(list_tag_tasks)
        if n_list_tag_tasks == 0:
           return 1
        
        output = ""
        try:
            # check precedenti
            src_dir_pregresso = Path(c.C_PATH_DIR_TASKS_GENERATI)
            pregresso_files = [f.name for f in src_dir_pregresso.iterdir() if f.is_file()]
            pregresso_n_files = len(pregresso_files)

            start_todo = pregresso_n_files
            end_todo = pregresso_n_files + max_task_alla_volta
            if end_todo >= n_list_tag_tasks:
                end_todo = n_list_tag_tasks
            tasks_todo = list_tag_tasks[start_todo:end_todo]
            task_from = tasks_todo[0]
            task_to = tasks_todo[len(tasks_todo) - 1]

            u.Log.msg("fase_1() => INIZIO")
            # leggi file documento tecnico da splittare
            doc_fase_0 = c.C_OUTPUT_FASE_0
            prompt = p.C_FASE_1.replace("$DIR", c.C_PATH_DIR_TASKS_GENERATI).replace("$DOC_FASE_0", doc_fase_0).replace("$C_OUT_DIR_IMPL", c.C_OUT_DIR_IMPL)
            if max_task_alla_volta > 1:
                prompt = prompt.replace("$C_FASE_1_TASK", p.C_FASE_1_PLURALE).replace("$TASK_SRC", task_from).replace("$TASK_DST", task_to)
            else:
                prompt = prompt.replace("$C_FASE_1_TASK", p.C_FASE_1_SINGOLO).replace("$TASK_SRC", task_from)
                    
            u.Log.msg(f"fase_1() => Divido il documento '{doc_fase_0}' in file task singoli [{task_from}-{task_to}] di {n_list_tag_tasks} totali.")
            status_modifiche = g.GitCheck.get_current_status(c.C_PATH_DIR_TASKS_GENERATI)
            output = a.Agente.run_pi(prompt)
            if not output:
                u.Log.msg("fase_1() => ERRORE, nessun output")
                new_src_dir_pregresso = Path(c.C_PATH_DIR_TASKS_GENERATI)
                new_pregresso_files = [f.name for f in new_src_dir_pregresso.iterdir() if f.is_file()]
                new_pregresso_n_files = len(new_pregresso_files)
                esistono_modifiche = g.GitCheck.check_current_status(c.C_PATH_DIR_TASKS_GENERATI, status_modifiche)
                if new_pregresso_n_files > pregresso_n_files or esistono_modifiche:
                    u.Log.msg("fase_1() => No output ma ha fatto progressi")
                    # l'esecuzione ha prodotto risultati
                    return 2
            else:
                # quanti microtask vanno ancora creati?
                src_dir_pregresso = Path(c.C_PATH_DIR_TASKS_GENERATI)
                pregresso_files = [f.name for f in src_dir_pregresso.iterdir() if f.is_file()]
                pregresso_n_files = len(pregresso_files)
                if pregresso_n_files < n_list_tag_tasks:
                    # serve generarne ancora altri
                    return 99
                u.Log.llm_model(output)
                u.Log.msg("fase_1() => FINE ok")
                return 0
        except KeyboardInterrupt:
            raise
        except Exception as e:
            u.Log.exc(e, "fase_1() => Exception")
        # errore
        return 1

    # TASKS_2_IMPL
    @staticmethod
    def fase_2(st_parametri=[]):
        output = ""
        try:
            # leggi i files task ed esegui il primo non completo
            dir_task = Path(c.C_PATH_DIR_TASKS_GENERATI)
            tasks = [f.name for f in dir_task.iterdir() if f.is_file()]
            tasks.sort(key=natural_sort_key)

            n_tasks = len(tasks)
            if n_tasks <= 0:
                u.Log.msg(f"fase_2() => Errore, nessun file/task generato dalla 'Fase 1'")
                return 9

            index_task = 0
            is_a_retry=False
            n_st_parametri = len(st_parametri)

            if n_st_parametri > 0:
                # indice nella lista dei file task da processare
                # (st_parametri[0] è l'ultimo file\task processato e terminato con successo)
                index_task = tasks.index(st_parametri[0])
                if n_st_parametri > 1:
                    # (st_parametri[1] è lo stato di elaborazione del file\task processato ['DONE' o 'PROGRESS'])
                    progresso = st_parametri[1]
                    if progresso == u.Log.V_DONE:
                        index_task = index_task + 1
                    elif progresso == u.Log.V_PROGRESS:
                        is_a_retry=True

            u.Log.msg(f"fase_2() => La 'Fase 1' ha generato {str(n_tasks)} files .md da elaborare")

            if is_a_retry:
                u.Log.msg(f"fase_2() => Il task '{tasks[index_task]}' era in corso in una run precedente, recupero e continuo")

            # recupero task da elaborare
            sf = tasks[index_task]
            path_task_da_elaborare = os.path.join(c.C_PATH_DIR_TASKS_GENERATI, sf)
            prompt = p.C_FASE_2.replace("$C_OUT_DIR_IMPL", c.C_OUT_DIR_IMPL).replace("$DOC_TASK_FASE_1", path_task_da_elaborare)
            if is_a_retry:
                prompt = prompt.replace("$RETRY", p.C_FASE_1_RETRY_TASK)
            else:
                prompt = prompt.replace("$RETRY", "")

            u.Log.msg(f"fase_2() => Implemento task '{tasks[index_task]}'")
            status_modifiche = g.GitCheck.get_current_status(c.C_OUT_DIR_IMPL)
            output = a.Agente.run_pi(prompt)
            if not output:
                u.Log.msg(f"fase_2() => ERRORE, nessun output (task '{tasks[index_task]}' [{(index_task+1)} di {n_tasks}])")
                # CONTROLLA SE CI SONO STATE MODIFICHE
                esistono_modifiche = g.GitCheck.check_current_status(c.C_OUT_DIR_IMPL, status_modifiche)
                if esistono_modifiche:
                    u.Log.msg(f"fase_2() => No output ma ha fatto progressi (task '{tasks[index_task]}' [{(index_task+1)} di {n_tasks}])")
                    # l'esecuzione ha prodotto risultati
                    # salvo stato progressi
                    u.Log.write_state_progress(2, u.Log.V_PROGRESS, [sf, u.Log.V_PROGRESS])
                    return 2
                else:
                    # l'esecuzione non ha prodotto progressi
                    u.Log.msg(f"fase_2() => No output e nessun progresso (task '{tasks[index_task]}' [{(index_task+1)} di {n_tasks}])")
                    return 1
            else:
                # task terminato con successo
                u.Log.llm_model(output)
                u.Log.msg(f"fase_2() => terminato => OK (task '{tasks[index_task]}' [{(index_task+1)} di {n_tasks}])")
                # salvo stato progressi
                u.Log.write_state_progress(2, u.Log.V_PROGRESS, [sf, u.Log.V_DONE])
                index_task = index_task + 1

                # CHECK: Se ogni task della 'Fase 2' è terminato => 'Fase 2' terminata OK
                if index_task >= n_tasks:
                    # Fase 2 => TERMINATA => salvo stato progressi
                    u.Log.write_state_progress(2, u.Log.V_DONE)
                    return 0
                else:
                    return 99
        except KeyboardInterrupt:
            raise
        except Exception as e:
            u.Log.exc(e, "fase_2() => Exception")
        # errore
        return 1
