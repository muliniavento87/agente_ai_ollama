import os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from mcp.server.mcpserver import MCPServer

# Base directory assoluta e sicura per il server MCP
#BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
#BASE_DIR = Path.cwd()
BASE_DIR = Path(__file__).resolve().parent.parent # / 'p'

mcp = MCPServer("Miei Tool Locali")

def _log_tools_mcp(name: str, t: str):
    timestamp = datetime.now(ZoneInfo("Europe/Rome")).strftime("%Y.%m.%d_%H.%M")
    # CRITICO CORRETTO: Uso del path assoluto anche per i log
    log_file = BASE_DIR / "metadati_loop" / ".LOG_TOOLS_MCP.md"
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
    """Scrive le righe nel file unendole con \n e forza la scrittura fisica su disco."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines) + ("\n" if lines else "")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())

@mcp.tool()
def crea_task_diario(testo: str) -> str:
    """
    Crea UN UNICO task nel diario per sessione. 
    Se il task esiste già, restituisce l'ID corrente senza generare errori bloccanti.
    
    Args:
        testo: La descrizione del progetto che vuoi creare.

    Results:
        id task/cartella creata.
    """
    _log_tools_mcp('crea_task_diario', testo)
    
    meta_dir = BASE_DIR / "metadati_loop"
    terminati_path = meta_dir / ".DIARIO_MANUALE_TERMINATI.md"
    attivi_path = meta_dir / ".DIARIO_MANUALE.md"

    meta_dir.mkdir(parents=True, exist_ok=True)
    if not terminati_path.exists():
        terminati_path.write_text("", encoding="utf-8")
    if not attivi_path.exists():
        attivi_path.write_text("", encoding="utf-8")

    terminati_lines = _read_lines(terminati_path)
    index = len(terminati_lines)
    
    # 1. Crea SEMPRE la cartella corrispondente all'indice per evitare che non venga generata
    task_dir = BASE_DIR / str(index)
    task_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Legge lo stato attivo
    attivi_lines = _read_lines(attivi_path)
    
    # 3. Se non è attivo, lo registra. Se è già attivo, evita di duplicarlo ma procede comunque.
    if not attivi_lines:
        timestamp = datetime.now().strftime("%Y.%m.%d_%H.%M")
        record = f"[{timestamp}] {testo}"
        attivi_lines.append(record)
        _write_lines(attivi_path, attivi_lines)
        _log_tools_mcp('crea_task_diario (nuovo ID)', str(index))
    else:
        _log_tools_mcp('crea_task_diario (già esistente, recuperato ID)', str(index))
    
    # Restituisce SEMPRE l'ID pulito (es. "0"), permettendo al modello di proseguire
    return str(index)

@mcp.tool()
def task_diario_non_terminato() -> list:
    """
    Usa questo tool per leggere il task non terminato nel diario.

    Results:
        array vuoto (nessun task da completare) o di 2 elementi [id, descrizione].
    """
    _log_tools_mcp('task_diario_non_terminato', '')

    attivi_path = BASE_DIR / "metadati_loop" / ".DIARIO_MANUALE.md"
    terminati_path = BASE_DIR / "metadati_loop" / ".DIARIO_MANUALE_TERMINATI.md"
    
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

    attivi_path = BASE_DIR / "metadati_loop" / ".DIARIO_MANUALE.md"
    terminati_path = BASE_DIR / "metadati_loop" / ".DIARIO_MANUALE_TERMINATI.md"
    
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
    
    return

if __name__ == "__main__":
    mcp.run()