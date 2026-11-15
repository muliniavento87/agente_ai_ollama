import hashlib
import subprocess
import os
from pathlib import Path
import datetime
import include.utils as u


class GitCheck:
    @staticmethod
    def _esegui_git(cmd, cwd):
        """Funzione di supporto per eseguire comandi git."""
        result = subprocess.run(
            cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout.strip()
    
    @staticmethod
    def _calcola_hash_working_tree(dir_path):
        """Scansiona tutti i file nella cartella (escluso .git),
        legge il loro percorso e contenuto, e restituisce un hash SHA-256
        preceduto da '_'.
        """
        hasher = hashlib.sha256()
        files_list = []

        for root, dirs, files in os.walk(dir_path):
            # Escludi la cartella .git
            if ".git" in root.split(os.sep):
                continue
            for file in sorted(files):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, dir_path)
                files_list.append((rel_path, full_path))

        # Ordina per percorso per garantire determinismo
        files_list.sort(key=lambda x: x[0])

        for rel_path, full_path in files_list:
            hasher.update(rel_path.encode("utf-8", errors="ignore"))
            try:
                with open(full_path, "rb") as f:
                    hasher.update(f.read())
            except Exception:
                pass  # Ignora file illeggibili o lockati

        return "_" + hasher.hexdigest()


    @staticmethod
    def get_current_status(dir_path):
        """Funzione A: Restituisce l'hash del commit HEAD (se pulito e presente)
        oppure un hash del working tree preceduto da '_' (se ci sono modifiche o nessun commit).
        """
        dir_path = os.path.abspath(dir_path)
        git_dir = os.path.join(dir_path, ".git")

        has_commit = False
        if os.path.exists(git_dir):
            res_head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=dir_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if res_head.returncode == 0:
                has_commit = True

        # Verifica se il repository è pulito (nessuna modifica pendente o file untracked)
        is_clean = False
        if has_commit:
            status_output = GitCheck._esegui_git(["git", "status", "--porcelain"], cwd=dir_path)
            if not status_output:
                is_clean = True

        # SEGNALE 1: C'è almeno un commit ed è tutto pulito -> Usa l'hash del commit HEAD
        if has_commit and is_clean:
            return GitCheck._esegui_git(["git", "rev-parse", "HEAD"], cwd=dir_path)
        
        # SEGNALE 2: Altrimenti (senza commit o con modifiche/file non tracciati) -> Usa l'hash dei file
        return GitCheck._calcola_hash_working_tree(dir_path)


    @staticmethod
    def check_current_status(dir_path, segnale):
        """Funzione B: Confronta lo stato attuale con il segnale e restituisce
        True se ci sono modifiche, False altrimenti.
        """
        dir_path = os.path.abspath(dir_path)

        # Se il segnale è un hash di commit (non inizia con '_')
        if not segnale.startswith("_"):
            commit_a = segnale
            # 1. Controlla nuovi commit fatti dallo script
            if GitCheck._esegui_git(["git", "log", f"{commit_a}..HEAD", "--oneline"], cwd=dir_path):
                return True
            # 2. Controlla modifiche nel working tree
            if GitCheck._esegui_git(["git", "status", "--porcelain"], cwd=dir_path):
                return True
            return False

        # Se il segnale è un hash del working tree (inizia con '_')
        else:
            # Ricalcola l'hash attuale dei file nella cartella e confrontalo.
            # L'hash riflette già l'intero stato (file nuovi, modificati, eliminati).
            hash_attuale = GitCheck._calcola_hash_working_tree(dir_path)
            return hash_attuale != segnale

    @staticmethod
    def test(d):
        # init repo git
        Git.init(d)

        #---- TRUE
        # 1. Lanci la Funzione "get_current_status()" prima dello script
        segnale_riferimento = GitCheck.get_current_status(d)
        # Esempio finto: creiamo un file per simulare una modifica
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "file_test.txt"), "w") as f:
            f.write("ciao")
        # 2. Lanci la Funzione "check_current_status()" dopo lo script
        modificato = GitCheck.check_current_status(d, segnale_riferimento)
        print(f"\nRisultato del controllo -> Modifiche avvenute? {modificato}")

        #---- FALSE
        segnale_riferimento = GitCheck.get_current_status(d)
        modificato = GitCheck.check_current_status(d, segnale_riferimento)
        print(f"\nRisultato del controllo -> Modifiche avvenute? {modificato}")

        #---- FALSE
        segnale_riferimento = GitCheck.get_current_status(d)
        modificato = GitCheck.check_current_status(d, segnale_riferimento)
        print(f"\nRisultato del controllo -> Modifiche avvenute? {modificato}")

        #---- TRUE
        segnale_riferimento = GitCheck.get_current_status(d)
        with open(os.path.join(d, "file_test.txt"), "a") as f:
            f.write("ciao")
        modificato = GitCheck.check_current_status(d, segnale_riferimento)
        print(f"\nRisultato del controllo -> Modifiche avvenute? {modificato}")

        #---- FALSE
        segnale_riferimento = GitCheck.get_current_status(d)
        modificato = GitCheck.check_current_status(d, segnale_riferimento)
        print(f"\nRisultato del controllo -> Modifiche avvenute? {modificato}")
    
class Git:
    @staticmethod
    def init(target_dir="."):
        try:
            # Percorso della cartella .git nella directory corrente
            cartella_git = Path(os.path.join(target_dir, ".git"))
            # check esistenza directory .git
            if not cartella_git.is_dir():
                # Esegue il comando git init
                subprocess.run(
                    ["git", "init"],
                    cwd=target_dir,
                    check=True
                )
        except Exception as e:
            u.Log.exc(e, "Git.init(...)")

    
    @staticmethod
    def check_modifiche(target_dir):
        output_modifiche = ""
        try:
            risultato = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                check=True
            )
            print(risultato)
            # Pulisce l'output da eventuali spazi o a capo superflui
            output_modifiche = risultato.stdout.strip()
            if output_modifiche:
                # trovate modifiche non committate
                print(output_modifiche)
                return True
        except Exception as e:
            u.Log.exc(e, "Git.check_modifiche(...)")
        return False
    
    @staticmethod
    def get_last_commit(target_dir):
        commit_hash = "None"
        try:
            # Recupera l'hash dell'ultimo commit
            risultato = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = risultato.stdout.strip()
            return commit_hash
        except Exception as e:
            # nessun commit
            u.Log.exc(e, "Git.get_last_commit(...)")
            return "None"
        
    @staticmethod
    def commit_all(target_dir):
        try:
            # 1. Genera il timestamp (es. 20261017_123045)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            messaggio_commit = f"m_{timestamp}"
            # 2. Aggiunge tutti i file modificati/nuovi (equivalente di git add .)
            subprocess.run(
                ["git", "add", "."],
                cwd=target_dir,
                check=True,
                capture_output=True
            )
            # 3. Esegue il commit
            subprocess.run(
                ["git", "commit", "-m", messaggio_commit],
                cwd=target_dir,
                check=True,
                capture_output=True
            )
        except Exception as e:
            # nessuna modifica da committare
            u.Log.exc(e, "Git.commit_all(...)")
