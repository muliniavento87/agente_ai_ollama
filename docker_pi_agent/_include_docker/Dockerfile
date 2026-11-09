# syntax=docker/dockerfile:1
# ═══════════════════════════════════════════════════════════════════
#  Container dev: Pi Agent + strumenti + Ollama (Host)
# ═══════════════════════════════════════════════════════════════════
FROM node:24-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# Installazione degli strumenti di sistema utili all'agente
RUN apt-get update && apt-get install -y --no-install-recommends \
      bash ca-certificates curl wget \
      git git-lfs openssh-client \
      python3 python3-pip python3-venv build-essential pkg-config \
      jq ripgrep fd-find tree unzip xz-utils file \
      procps lsof iproute2 \
      bubblewrap socat \
    && rm -rf /var/lib/lists/* \
    && ln -s "$(command -v fdfind)" /usr/local/bin/fd

# Installazione di huggingface CLI[cite: 1]
RUN python3 -m pip install --no-cache-dir --break-system-packages -U \
      pip "huggingface_hub[cli]" hf_transfer

# Installazione globale di Pi Agent[cite: 1]
RUN npm install -g --unsafe-perm --ignore-scripts @earendil-works/pi-coding-agent

# 4070  172.19.16.1
# 5050  172.22.16.1
# Creazione della cartella di configurazione
RUN mkdir -p /root/.pi/agent

# Copia diretta dei file di configurazione
COPY models.json /root/.pi/agent/models.json
COPY settings.json /root/.pi/agent/settings.json
COPY auth.json /root/.pi/agent/auth.json
COPY mcp.json /root/.pi/agent/mcp.json
#COPY sandbox.json /root/.pi/agent/sandbox.json

# (Pi Agent) plugin:
#   - mostra token al secondo
#    pi install https://github.com/gsanhueza/pi-token-speed
#   - pi-atelier (dashboard con tante informazioni dettagliate, automatico)
#    pi install npm:pi-atelier
#   - pi-web-access (recupera info da internet, in autonomia se serve)
#    pi install npm:pi-web-access
#   - pi-hermes-memory (salva uno storico dei contenuti chat in database 
#    pi install npm:pi-hermes-memory
#   - context-mode (gestione contesto, in automatico riduce l'occupazione)
#    pi install npm:context-mode
RUN pi install https://github.com/gsanhueza/pi-token-speed && \
    pi install npm:pi-atelier && \
    # pi install npm:pi-sandbox && \
    pi install npm:pi-mcp-extension

# Integrazione Skill mattpocock
RUN git clone https://github.com/mattpocock/skills.git /root/.pi/agent/skills/mattpocock || true

# Preconfigurazione di Git[cite: 1]
RUN git config --global --add safe.directory '*' && \
    git config --global user.name "Pi Agent" && \
    git config --global user.email "pi-agent@local.dev"

# WORKDIR /scripts
WORKDIR /workspace
