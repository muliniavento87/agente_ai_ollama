#!/bin/bash

# Controlla se è stata passata una stringa come argomento
if [ -z "$1" ]; then
    echo "Uso: $0 \"la tua stringa\""
    exit 1
fi

PROMPT="$1"
MODEL="Ornith-1.5-9b-IQ3-M-8k"
URL="http://localhost:11434/api/generate"

# Crea il payload JSON in modo sicuro usando jq
PAYLOAD=$(jq -n \
    --arg model "$MODEL" \
    --arg prompt "$PROMPT" \
    '{model: $model, prompt: $prompt, stream: false}')

# Invia la richiesta a Ollama tramite curl
RESPONSE_JSON=$(curl -s -X POST "$URL" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

#echo "---------------"
#echo $RESPONSE_JSON
#echo "---------------"

# Estrae il testo della risposta e lo assegna alla variabile
RISPOSTA_OLLAMA=$(echo "$RESPONSE_JSON" | jq -r '.response')

# Stampa la risposta a schermo
echo "$RISPOSTA_OLLAMA"