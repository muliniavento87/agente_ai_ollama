#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  Entrypoint del container "server" (fork PrismML-Eng/llama.cpp)
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

# ── 1. binario del fork ──────────────────────────────────────────────
BIN="$(find /opt/llama -type f -name llama-server 2>/dev/null | head -n1)"
if [ -z "${BIN}" ]; then
  echo "ERROR: llama-server non trovato in /opt/llama" >&2
  exit 1
fi
BIN_DIR="$(cd "$(dirname "${BIN}")" && pwd)"
export LD_LIBRARY_PATH="${BIN_DIR}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
echo ">>> Fork llama.cpp binario: ${BIN}"

# ── 2. GPU ────────────────────────────────────────────────────────────
LLAMA_BIN="${LLAMA_BIN:-cuda}"
if [ "${LLAMA_BIN}" = "cuda" ] && command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader || true
fi

# ── 3. Selezione modello tramite MODELLO_ATTIVO ───────────────────────
# https://prismml.com/news/bonsai-2-family
# 0 = Ternary-Bonsai-2-27B
# 1 = Ternary-Bonsai-2-9B
# 2 = Ternary-Bonsai-2-4B
MODELLO_ATTIVO="${MODELLO_ATTIVO:-2}"

if [ "${MODELLO_ATTIVO}" = "0" ]; then
  # modello grande (27b, derivato da qwen3.8 27b)
  MODEL_REPO="prism-ml/Ternary-Bonsai-2-27B-gguf"
  MODEL_FILE="Ternary-Bonsai-2-27B-PTQ1_0.gguf"
elif [ "${MODELLO_ATTIVO}" = "1" ]; then
  # modello medio (9b, derivato da Qwen3.5 9b)
  MODEL_REPO="prism-ml/Ternary-Bonsai-2-9B-gguf"
  MODEL_FILE="Ternary-Bonsai-2-9B-PTQ1_0.gguf"
elif [ "${MODELLO_ATTIVO}" = "2" ]; then
  # modello piccolo (4b, derivato da Qwen3.5 4b)
  MODEL_REPO="prism-ml/Ternary-Bonsai-2-4B-gguf"
  MODEL_FILE="Ternary-Bonsai-2-4B-PTQ1_0.gguf"
else
  # DEFAULT => modello grande (27b)
  MODEL_REPO="prism-ml/Ternary-Bonsai-2-27B-gguf"
  MODEL_FILE="Ternary-Bonsai-2-27B-PTQ1_0.gguf"
fi

MODEL_DIR="${MODEL_DIR:-/models}"

mkdir -p "${MODEL_DIR}"
if [ -f "${MODEL_DIR}/${MODEL_FILE}" ]; then
  echo ">>> Modello già presente (nessun nuovo download): ${MODEL_DIR}/${MODEL_FILE} ($(du -h "${MODEL_DIR}/${MODEL_FILE}" | cut -f1))"
else
  echo ">>> Download di ${MODEL_FILE} (${MODEL_REPO}) → ${MODEL_DIR}/ ..."
  curl -fL --retry 5 --retry-delay 5 -C - --progress-bar \
    -o "${MODEL_DIR}/${MODEL_FILE}.part" \
    "https://huggingface.co/${MODEL_REPO}/resolve/main/${MODEL_FILE}"
  mv "${MODEL_DIR}/${MODEL_FILE}.part" "${MODEL_DIR}/${MODEL_FILE}"
  echo ">>> Download completato"
fi

# ── 4. flag di avvio (ROUTER MODE) ────────────────────────────────────
PORT="${PORT:-8080}"
NGL="${LLAMA_NGL:-99}"
FLASH="${LLAMA_FLASH_ATTN:-on}"

if [ "${LLAMA_BIN}" = "cpu" ]; then
  NGL=0
  FLASH=off
fi

LLAMA_CTX="${LLAMA_CTX:-2048}"
LLAMA_CACHE_K="${LLAMA_CACHE_TYPE_K:-q8_0}"
LLAMA_CACHE_V="${LLAMA_CACHE_TYPE_V:-q8_0}"
LLAMA_BATCH="${LLAMA_BATCH:-2048}"

# ── 4.b AUTO-FIT memoria (solo build CPU) ────────────────────────────
if [ "${LLAMA_BIN}" = "cpu" ] && command -v python3 >/dev/null 2>&1 && [ -f "${MODEL_DIR}/${MODEL_FILE}" ]; then
  if MEM_JSON="$(python3 /usr/local/bin/llama-gguf-mem.py "${MODEL_DIR}/${MODEL_FILE}" \
        --ctx "${LLAMA_CTX}" --cache "${LLAMA_CACHE_K}" --batch "${LLAMA_BATCH}" 2>/dev/null)"; then
    IFS=$'\t' read -r MEM_FITS MEM_TOTAL MEM_AVAIL MEM_REQ_CTX MEM_SUG_CTX MEM_SUG_CACHE MEM_SUG_BATCH MEM_NOTE MEM_TOT_H MEM_AVAIL_H <<< \
      "$(printf '%s' "${MEM_JSON}" | python3 -c '
import json,sys
d = json.load(sys.stdin)
e = d.get("estimate", {}); s = d.get("suggested", {}); r = d.get("requested", {})
print("\t".join(str(x) for x in [
  d.get("fits"), int(e.get("total_bytes", 0)), int(d.get("mem_available", 0)),
  int(r.get("ctx", 0)), int(s.get("ctx", 0)), s.get("cache", ""), int(s.get("batch", 0)),
  ("; ".join(d.get("notes", [])) or "-"), d.get("total_human", ""), d.get("mem_available_human", "")]))
' 2>/dev/null)"
    if [ -n "${MEM_TOTAL:-}" ] && [ "${MEM_TOTAL:-0}" -gt 0 ] 2>/dev/null; then
      if [ "${MEM_AVAIL:-0}" -le 0 ] 2>/dev/null; then
        echo "ATTENZIONE: memoria disponibile sconosciuta, avvio senza auto-fit." >&2
      elif [ "${MEM_FITS}" = "True" ]; then
        LLAMA_CTX="${MEM_SUG_CTX}"
        LLAMA_CACHE_K="${MEM_SUG_CACHE}"
        LLAMA_CACHE_V="${MEM_SUG_CACHE}"
        LLAMA_BATCH="${MEM_SUG_BATCH}"
      else
        echo "ERROR: il modello non sta in RAM." >&2
        exit 1
      fi
    fi
  fi
fi

ARGS=(--models-dir "${MODEL_DIR}")
ARGS+=(--host 0.0.0.0 --port "${PORT}")
ARGS+=(--ctx-size "${LLAMA_CTX}")
ARGS+=(--parallel "${LLAMA_PARALLEL:-1}")
ARGS+=(--cache-type-k "${LLAMA_CACHE_K}")
ARGS+=(--cache-type-v "${LLAMA_CACHE_V}")
ARGS+=(--batch-size "${LLAMA_BATCH}")
ARGS+=(--ubatch-size "${LLAMA_BATCH}")
ARGS+=(--n-gpu-layers "${NGL}")
if [ "${FLASH}" = "on" ]; then
  ARGS+=(--flash-attn on)
fi
if [ -n "${LLAMA_THREADS:-}" ]; then
  ARGS+=(--threads "${LLAMA_THREADS}")
fi
ARGS+=(--jinja)
ARGS+=(--no-models-autoload)
ARGS+=(--temp "${LLAMA_TEMP:-1.0}")
ARGS+=(--top-p "${LLAMA_TOP_P:-0.95}")
ARGS+=(--top-k "${LLAMA_TOP_K:-20}")
if [ -n "${LLAMA_API_KEY:-}" ]; then
  ARGS+=(--api-key "${LLAMA_API_KEY}")
fi
if [ -n "${LLAMA_EXTRA_ARGS:-}" ]; then
  read -r -a EXTRA <<< "${LLAMA_EXTRA_ARGS}"
  ARGS+=("${EXTRA[@]}")
fi

# ── 5. avvio del server + preload ─────────────────────────────────────
echo ">>> Avvio llama-server (router mode, bin=${LLAMA_BIN}, ctx=${LLAMA_CTX}, np=${LLAMA_PARALLEL:-1}, ngl=${NGL}, batch=${LLAMA_BATCH})"
SERVER_LOG="${SERVER_LOG:-/tmp/llama-server.log}"
"${BIN}" "${ARGS[@]}" 2>&1 | tee "${SERVER_LOG}" &
SERVER_PID=$!
cleanup() { echo ">>> Arresto del server (pid ${SERVER_PID})"; kill "${SERVER_PID}" 2>/dev/null; wait "${SERVER_PID}" 2>/dev/null; exit 0; }
trap cleanup INT TERM

for _ in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then break; fi
  if ! kill -0 "${SERVER_PID}" 2>/dev/null; then
    echo "ERROR: llama-server è terminato prematuramente." >&2
    tail -n 30 "${SERVER_LOG}" 2>/dev/null >&2 || true
    exit 1
  fi
  sleep 1
done

if [ "${LLAMA_PRELOAD:-1}" = "1" ]; then
  MODEL_BASENAME="${MODEL_FILE%.gguf}"
  MODEL_ID="$(curl -fsS "http://127.0.0.1:${PORT}/models" 2>/dev/null \
    | LLAMA_MODEL_BASENAME="${MODEL_BASENAME}" python3 -c '
import json, os, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print(""); sys.exit(0)
data = d.get("data", []) if isinstance(d, dict) else []
base = os.environ["LLAMA_MODEL_BASENAME"]
m = next((x for x in data if x.get("id") == base), None)
if not m and data:
    m = data[0]
print(m.get("id", "") if m else "")
')"
  if [ -n "${MODEL_ID}" ]; then
    echo ">>> Preload del modello: ${MODEL_ID}..."
    curl -sS -X POST "http://127.0.0.1:${PORT}/models/load" \
      -H 'Content-Type: application/json' \
      -d "{\"model\":\"${MODEL_ID}\"}" >/dev/null || true
    for _ in $(seq 1 600); do
      STATUS="$(curl -fsS "http://127.0.0.1:${PORT}/models" 2>/dev/null \
        | LLAMA_MODEL_ID="${MODEL_ID}" python3 -c '
import json, os, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print(""); sys.exit(0)
data = d.get("data", []) if isinstance(d, dict) else []
mid = os.environ["LLAMA_MODEL_ID"]
m = next((x for x in data if x.get("id") == mid), None)
print(m.get("status", {}).get("value", "") if m else "")
')"
      if [ "${STATUS}" = "loaded" ]; then
        echo ">>> Modello caricato con successo"
        break
      fi
      if [ "${STATUS}" = "failed" ]; then
        echo "ERROR: caricamento fallito" >&2
        break
      fi
      kill -0 "${SERVER_PID}" 2>/dev/null || break
      sleep 2
    done
  fi
fi

wait "${SERVER_PID}"