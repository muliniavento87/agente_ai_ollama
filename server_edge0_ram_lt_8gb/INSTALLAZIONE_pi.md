# Pi Agent: setup iniziale (globale)
npm install -g --unsafe-perm --ignore-scripts @earendil-works/pi-coding-agent

# Pi Agent: inizializza cartelle e configurazione
- crea cartella
mkdir -p ~/.pi/agent
- copia dentro i files della cartella ".pi/agent" (presenti qui)
open ~/.pi/agent

# Pi Agent: estensioni
pi install https://github.com/gsanhueza/pi-token-speed && \
pi install npm:pi-atelier
