import inspect
import os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from mcp.server.mcpserver import MCPServer


# Base directory assoluta e sicura per il server MCP
#BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
#BASE_DIR = Path.cwd()
BASE_DIR = Path(__file__).resolve().parent.parent

# Dizionario globale che si popolerà da solo
AVAILABLE_TOOLS = {}

def auto_tool(func):
    """
    Decoratore personalizzato che registra automaticamente la funzione 
    sia nel server MCP sia nel dizionario dei tool disponibili per l'agente.
    """
    # 1. Registra la funzione nel dizionario automatico usando il suo nome
    AVAILABLE_TOOLS[func.__name__] = func
    # 2. La registra anche come tool ufficiale MCP (usando il decoratore nativo)
    return mcp.tool()(func)

# --- I TUOI SERVIZI ---

mcp = MCPServer("Miei Tool Locali")

# ATTENZIONE!!! Da questo momento in poi, ogni volta che vorrai aggiungere un nuovo servizio (es. un tool per inviare email, cancellare file, ecc.), ti basterà scrivere
#@auto_tool
def mio_nuovo_servizio(parametro: str) -> str:
    """Descrizione chiara di cosa fa il servizio per l'LLM."""
    # Tua logica qui...
    return "fatto"

@auto_tool
def test(parametro: str) -> str:
    """
    Questo tool crea un file col nome '<parametro>.md'.
    Se la funzione termina con successo riceverai la stringa 'fatto'.

    Args:
        parametro: il nome usato sul file da creare. 
    """
    fl = BASE_DIR / f"{parametro}.md"
    fl.write_text("", encoding="utf-8")
    return "fatto"



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

@auto_tool
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

@auto_tool
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

@auto_tool
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


# --- GENERATORE AUTOMATICO DEL CATALOGO OPENAI ---

# 2. Funzione di supporto per convertire i tipi Python nei tipi JSON Schema di OpenAI
def _python_type_to_json_type(param_type):
    if param_type == int: return "integer"
    elif param_type == float: return "number"
    elif param_type == bool: return "boolean"
    elif param_type == list: return "array"
    elif param_type == dict: return "object"
    return "string"

def get_openai_tools_definition() -> list[dict]:
    tools = []
    for name, func in AVAILABLE_TOOLS.items():
        doc = inspect.getdoc(func) or "Nessuna descrizione."
        sig = inspect.signature(func)
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
            json_type = _python_type_to_json_type(param_type)
            
            properties[param_name] = {
                "type": json_type,
                "description": f"Parametro {param_name} per {name}"
            }
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
                
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": doc,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        })
    return tools

if __name__ == "__main__":
    mcp.run()