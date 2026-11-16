#!/bin/bash

# Interrompi lo script se un comando restituisce un errore
set -e

# Vai nella cartella dello script (run_docker/mac/) e poi sali di 2 livelli (Root del progetto)
cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

# apro il server del modello in una nuova finestra (perchè deve rimanere aperta)
echo "==> Avvio di host-llama-macos.sh in una NUOVA finestra del Terminale..."
osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR' && ./host-llama-macos.sh\""
