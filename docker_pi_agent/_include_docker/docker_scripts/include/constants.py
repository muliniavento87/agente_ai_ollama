import os

# --- dir
C_OUT_DIR_IMPL = "output/"
C_THIS_SCRIPT_INCLUDE = "include/"
C_PATH_DIR_METADATI = ".metadati/"
# --- files
C_THIS_SCRIPT = "workflow_auto.py"
C_FILE_OUTPUT_FASE_0 = "OUTPUT_FASE_0.md"

C_PATH_FILE_OUTPUT_FASE_0 = os.path.join(C_OUT_DIR_IMPL, C_FILE_OUTPUT_FASE_0)
C_OUTPUT_FASE_0 = os.path.join(C_PATH_DIR_METADATI, C_FILE_OUTPUT_FASE_0)
C_CURRENT_PROMPT = os.path.join(C_PATH_DIR_METADATI, "CURRENT_PROMPT.md")
C_PATH_DIR_TASKS_GENERATI = os.path.join(C_PATH_DIR_METADATI, ".task_generati/")
C_LOG_FILE = os.path.join(C_PATH_DIR_METADATI, "LOG.md")
C_STATO_ELAB = os.path.join(C_PATH_DIR_METADATI, "STATE.json")

# "Pi Agent" deve ignorare questi files e cartella
C_FILES_CARTELLE_DA_IGNORARE = [
    C_THIS_SCRIPT,
    C_PATH_DIR_METADATI,
    C_THIS_SCRIPT_INCLUDE,
]
C_IGNORARE = "".join(f"- {obj}\n" for obj in C_FILES_CARTELLE_DA_IGNORARE)