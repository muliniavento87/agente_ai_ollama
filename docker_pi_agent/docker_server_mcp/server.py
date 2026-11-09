import os
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from mcp.server.mcpserver import MCPServer

# Base directory assoluta e sicura per il server MCP
#BASE_DIR = Path.cwd()
#BASE_DIR = Path(__file__).resolve().parent.parent / 'p'
#BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
#BASE_DIR = Path(__file__).resolve().parent.parent # ora punta a "/"
BASE_DIR = Path("/").resolve()

# files
DIR_WORKSPACE = 'workspace'
DIR_METADATI = 'workspace_metadati'
FILE_LOG_MCP = 'LOG_TOOLS_MCP.md'
FILE_TASK_IN_CORSO = 'TASK_IN_CORSO.md'
FILE_TASK_TERMINATI = 'TASK_TERMINATI.md'
# paths
PATH_DIR_WORKSPACE = BASE_DIR / DIR_WORKSPACE
PATH_DIR_METADATI = BASE_DIR / DIR_METADATI
PATH_FILE_LOG_MCP = BASE_DIR / DIR_METADATI / FILE_LOG_MCP
PATH_FILE_TASK_IN_CORSO = BASE_DIR / DIR_METADATI / FILE_TASK_IN_CORSO
PATH_FILE_TASK_TERMINATI = BASE_DIR / DIR_METADATI / FILE_TASK_TERMINATI

mcp = MCPServer("Miei Tool Locali")

def _log_tools_mcp(name: str, t: str):
    timestamp = datetime.now(ZoneInfo("Europe/Rome")).strftime("%Y.%m.%d_%H.%M")
    # CRITICO CORRETTO: Uso del path assoluto anche per i log
    log_file = PATH_FILE_LOG_MCP #BASE_DIR / "metadati_loop" / ".LOG_TOOLS_MCP.md"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    if not log_file.exists():
        log_file.write_text("", encoding="utf-8")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] Tool => {name}\nMsg => {t}\n-------------\n")

def _read_lines(filepath: Path) -> list[str]:
    """Legge il file restituendo una lista di righe pulite (senza newline)."""
    if not filepath.exists():
        return []
    content = filepath.read_text(encoding="utf-8")
    if not content:
        return []
    return [line.rstrip("\n") for line in content.splitlines()]

def _write_lines(filepath: Path, lines: list[str]):
    """Scrive le righe nel file unendole con \n senza aggiungere un newline finale."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines)  # Nessun + ("\n" if lines else "")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())

@mcp.tool()
def crea_task_diario(testo: str) -> str:
    """
    Crea UN UNICO task nel diario per sessione. 
    Se il task esiste già, restituisce un errore bloccante e non crea nulla.
    
    Args:
        testo: La descrizione del progetto che vuoi creare.

    Results:
        id task creato o messaggio di errore se esiste già un task attivo.
    """
    _log_tools_mcp('crea_task_diario', testo)
    
    terminati_path = PATH_FILE_TASK_TERMINATI
    attivi_path = PATH_FILE_TASK_IN_CORSO

    terminati_lines = _read_lines(terminati_path)
    index = len(terminati_lines)
    
    # 1. Legge lo stato attivo prima di fare qualsiasi cosa
    attivi_lines = _read_lines(attivi_path)
    
    # 2. SE ESRA GIÀ UN TASK ATTIVO -> BLOCCO E RESTITUISCO UN ERRORE ESPLICITO ALL'LLM
    if attivi_lines:
        task_corrente = attivi_lines[0]
        _log_tools_mcp('crea_task_diario (RIFIUTATO - task già esistente)', task_corrente)
        return (
            f"ERRORE OPERATIVO: Impossibile creare un nuovo task perché ne esiste già uno in corso: '{task_corrente}'. "
            f"Non devi chiamare 'crea_task_diario'. Lavora con il task esistente o usa 'completa_task_diario' "
            f"se hai finito. Procedi utilizzando il task attuale."
        )
    
    # 3. Se non è attivo, procede alla creazione della cartella e del record
    task_dir = PATH_DIR_WORKSPACE / str(index)
    task_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y.%m.%d_%H.%M")
    record = f"[{timestamp}] {testo}"
    attivi_lines.append(record)
    _write_lines(attivi_path, attivi_lines)
    _log_tools_mcp('crea_task_diario (nuovo ID)', str(index))
    
    return str(index)

@mcp.tool()
def task_diario_non_terminato() -> list:
    """
    Usa questo tool per leggere il task non terminato nel diario.

    Results:
        array vuoto (nessun task da completare) o di 2 elementi [id, descrizione].
    """
    _log_tools_mcp('task_diario_non_terminato', '')

    terminati_path = PATH_FILE_TASK_TERMINATI
    attivi_path = PATH_FILE_TASK_IN_CORSO
    
    lines = _read_lines(attivi_path)
    if not lines:
        return []
    
    terminati_lines = _read_lines(terminati_path)
    num_terminati = len(terminati_lines)
    
    return [str(num_terminati), lines[0]]

@mcp.tool()
def completa_task_diario() -> None:
    """
    Usa questo tool per flaggare come completato un task nel diario.
    """
    _log_tools_mcp('completa_task_diario', '')

    terminati_path = PATH_FILE_TASK_TERMINATI #meta_dir / ".DIARIO_MANUALE_TERMINATI.md"
    attivi_path = PATH_FILE_TASK_IN_CORSO #meta_dir / ".DIARIO_MANUALE.md"
    
    attivi_lines = _read_lines(attivi_path)
    if not attivi_lines:
        return
    
    # Rimuove la prima riga dai task attivi
    first_line = attivi_lines.pop(0)
    _write_lines(attivi_path, attivi_lines)
    
    # Accoda la riga ai task terminati
    terminati_lines = _read_lines(terminati_path)
    terminati_lines.append(first_line)
    _write_lines(terminati_path, terminati_lines)

if __name__ == "__main__":
    mcp.run()