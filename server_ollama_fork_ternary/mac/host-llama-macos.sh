#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
#  Avvio nativo di llama-server (fork PrismML-Eng) su macOS con GPU Metal
# ═══════════════════════════════════════════════════════════════════════
set -euo pipefail

# ── Configurazione ─────────────────────────────────────────────────────
PRISM_REPO="PrismML-Eng/llama.cpp"
# identifica il TAG più recente
#   - "curl -s https://api.github.com/repos/PrismML-Eng/llama.cpp/releases/latest | grep '"tag_name"'"
#   - metti il nuovo tag in  PRISM_LLAMA_TAG=""
#   - rimuovi vecchio binario LLAMA
#     - "rm -rf ~/.local/llama-prism"
PRISM_LLAMA_TAG="prism-b10709-9a9394a"
PRISM_LLAMA_TAG="prism-b12128-d7b2896"
LLAMA_HOST_DIR="${HOME}/.local/llama-prism"
BIN="${LLAMA_HOST_DIR}/llama-server"

MODEL_DIR="${PWD}/models"

# https://prismml.com/news/bonsai-2-family
#
# 0 = Ternary-Bonsai-2-27B
# 1 = Ternary-Bonsai-2-9B
# 2 = Ternary-Bonsai-2-4B
MODELLO_ATTIVO="2"

# DEFAULT
MODEL_REPO=""
MODEL_FILE=""

if [[ "$MODELLO_ATTIVO" == "0" ]]; then
  # modello grande (27b, derivato da qwen3.8 27b)
  MODEL_REPO="prism-ml/Ternary-Bonsai-2-27B-gguf"
  MODEL_FILE="Ternary-Bonsai-2-27B-PTQ1_0.gguf"

elif [[ "$MODELLO_ATTIVO" == "1" ]]; then
  # modello medio (9b, derivato da Qwen3.5 9b)
  MODEL_REPO="prism-ml/Ternary-Bonsai-2-9B-gguf"
  MODEL_FILE="Ternary-Bonsai-2-9B-PTQ1_0.gguf"

elif [[ "$MODELLO_ATTIVO" == "2" ]]; then
  # modello piccolo (4b, derivato da Qwen3.5 4b)
  MODEL_REPO="prism-ml/Ternary-Bonsai-2-4B-gguf"
  MODEL_FILE="Ternary-Bonsai-2-4B-PTQ1_0.gguf"
else
  # DEFAULT => modello grande (27b, derivato da qwen3.8 27b)
  MODEL_REPO="prism-ml/Ternary-Bonsai-2-27B-gguf"
  MODEL_FILE="Ternary-Bonsai-2-27B-PTQ1_0.gguf"
fi


# Rete
HOST_BIND="127.0.0.1"   # Usa 0.0.0.0 se usi Colima al posto di Docker Desktop
PORT="8080"
LLAMA_API_KEY=""        # Opzionale (consigliata se esponi su 0.0.0.0)

# Parametri Modello & Memoria
LLAMA_CTX="32768"       # Su Mac 16GB RAM scendi a 16384 o 8192 se saturi la memoria
LLAMA_PARALLEL="1"
# ctk => "MOLTO" sensibile alla variazione di quantizzazione tra q8_0 e q4_0
# (metti q8_0, variazione di circa 200mb su 32k contesto, ma la qualità sale molto su contesti lunghi)
LLAMA_CACHE_TYPE_K="q8_0"
# ctv => "POCO" sensibile alla variazione di quantizzazione tra q8_0 e q4_0 (lascia q4_0)
LLAMA_CACHE_TYPE_V="q4_0"
LLAMA_BATCH="2048"
LLAMA_NGL="99"

# Parametri Sampling (consigliati per Bonsai 2 27B)
LLAMA_TEMP="0.6"
LLAMA_TOP_P="0.95"
LLAMA_TOP_K="20"
LLAMA_EXTRA_ARGS=""     # Es. "--reasoning-budget 64"

# ── 1. Verifica architettura macOS ─────────────────────────────────────
MAC_ARCH="$(uname -m)"
case "${MAC_ARCH}" in
  arm64|aarch64) ASSET_ARCH="arm64" ;;
  x86_64)        ASSET_ARCH="x64" ;;
  *) echo "ERRORE: architettura macOS non riconosciuta: ${MAC_ARCH}" >&2; exit 1 ;;
esac
ASSET="llama-${PRISM_LLAMA_TAG}-bin-macos-${ASSET_ARCH}.tar.gz"
ASSET_URL="https://github.com/${PRISM_REPO}/releases/download/${PRISM_LLAMA_TAG}/${ASSET}"

# ── 2. Verifica e download automatico del modello ──────────────────────
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"
MODEL_URL="https://huggingface.co/${MODEL_REPO}/resolve/main/${MODEL_FILE}"

if [ ! -f "${MODEL_PATH}" ]; then
  echo ">>> Modello non trovato in ${MODEL_PATH}."
  echo ">>> Scarico ${MODEL_FILE} da Hugging Face (~5.95 GB)..."
  mkdir -p "${MODEL_DIR}"
  TMP_MODEL="${MODEL_PATH}.part"

  if curl -fL --retry 3 --retry-delay 5 -# -C - -o "${TMP_MODEL}" "${MODEL_URL}"; then
    mv "${TMP_MODEL}" "${MODEL_PATH}"
    echo ">>> Download modello completato: ${MODEL_PATH}"
  else
    echo "ERRORE: impossibile scaricare il modello da ${MODEL_URL}" >&2
    exit 1
  fi
fi

# ── 3. Installazione binario (solo al primo avvio) ─────────────────────
if [ ! -x "${BIN}" ]; then
  echo ">>> Scarico ${ASSET} (${ASSET_ARCH}, supporto Metal)..."
  mkdir -p "${LLAMA_HOST_DIR}"
  curl -fL --retry 3 --retry-delay 5 -o "${LLAMA_HOST_DIR}/${ASSET}" "${ASSET_URL}"
  tar -xzf "${LLAMA_HOST_DIR}/${ASSET}" -C "${LLAMA_HOST_DIR}" --strip-components=1
  rm -f "${LLAMA_HOST_DIR}/${ASSET}"
  
  if command -v xattr >/dev/null 2>&1; then
    xattr -dr com.apple.quarantine "${LLAMA_HOST_DIR}" 2>/dev/null || true
  fi
  chmod +x "${BIN}"
  echo ">>> Installato in ${LLAMA_HOST_DIR}/"
fi

if [ "${1:-}" = "--install-only" ]; then
  echo ">>> Installazione completata. Avvia con: ${0}"
  exit 0
fi

# ── 4. Avvio del server ────────────────────────────────────────────────
echo ">>> Avvio llama-server (Metal, ctx=${LLAMA_CTX}, bind=${HOST_BIND}:${PORT})"

API_ARGS=()
[ -n "${LLAMA_API_KEY}" ] && API_ARGS=(--api-key "${LLAMA_API_KEY}")

EXTRA_ARGS=()
[ -n "${LLAMA_EXTRA_ARGS}" ] && read -r -a EXTRA_ARGS <<< "${LLAMA_EXTRA_ARGS}"

FLASH_ARGS=()
[ "${ASSET_ARCH}" = "arm64" ] && FLASH_ARGS=(--flash-attn on)

"${BIN}" \
  --models-dir "${MODEL_DIR}" \
  --alias "${MODEL_FILE%.gguf}" \
  --host "${HOST_BIND}" \
  --port "${PORT}" \
  --ctx-size "${LLAMA_CTX}" \
  --parallel "${LLAMA_PARALLEL}" \
  --cache-type-k "${LLAMA_CACHE_TYPE_K}" \
  --cache-type-v "${LLAMA_CACHE_TYPE_V}" \
  --batch-size "${LLAMA_BATCH}" \
  --ubatch-size 512 \
  --n-gpu-layers "${LLAMA_NGL}" \
  ${FLASH_ARGS[@]+"${FLASH_ARGS[@]}"} \
  --jinja \
  --no-models-autoload \
  --temp "${LLAMA_TEMP}" \
  --top-p "${LLAMA_TOP_P}" \
  --top-k "${LLAMA_TOP_K}" \
  ${API_ARGS[@]+"${API_ARGS[@]}"} \
  ${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"} &

SERVER_PID=$!

cleanup() {
  echo ">>> Arresto del server (PID ${SERVER_PID})..."
  kill "${SERVER_PID}" 2>/dev/null || true
  wait "${SERVER_PID}" 2>/dev/null || true
  exit 0
}
trap cleanup INT TERM

# Attesa healthcheck
for _ in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then break; fi
  if ! kill -0 "${SERVER_PID}" 2>/dev/null; then
    echo "ERRORE: llama-server terminato prematuramente." >&2
    exit 1
  fi
  sleep 1
done

# ── 5. Preload del modello ─────────────────────────────────────────────
MODEL_ID="${MODEL_FILE%.gguf}"
if command -v python3 >/dev/null 2>&1; then
  echo ">>> Preload del modello: ${MODEL_ID}..."
  curl -sS -X POST "http://127.0.0.1:${PORT}/models/load" \
    -H 'Content-Type: application/json' \
    -d "{\"model\":\"${MODEL_ID}\"}" >/dev/null || true

  for _ in $(seq 1 300); do
    STATUS="$(curl -fsS "http://127.0.0.1:${PORT}/models" 2>/dev/null \
      | LLAMA_MODEL_ID="${MODEL_ID}" python3 -c '
import json, os, sys
try:
    d = json.load(sys.stdin)
    data = d.get("data", []) if isinstance(d, dict) else []
    m = next((x for x in data if x.get("id") == os.environ["LLAMA_MODEL_ID"]), None)
    print(m.get("status", {}).get("value", "") if m else "")
except Exception:
    print("")
')"
    if [ "${STATUS}" = "loaded" ]; then
      echo ">>> Modello pronto su http://${HOST_BIND}:${PORT} (GPU Metal attiva)."
      break
    elif [ "${STATUS}" = "failed" ]; then
      echo "ERRORE: caricamento del modello fallito." >&2
      exit 1
    fi
    kill -0 "${SERVER_PID}" 2>/dev/null || { echo "ERRORE: server terminato." >&2; exit 1; }
    sleep 2
  done
else
  echo "ATTENZIONE: python3 non trovato, il modello verrà caricato alla prima richiesta." >&2
fi

echo ">>> Server attivo (Ctrl-C per fermarlo)."
wait "${SERVER_PID}"