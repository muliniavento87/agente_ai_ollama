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
    && rm -rf /var/lib/apt/lists/* \
    && ln -s "$(command -v fdfind)" /usr/local/bin/fd

# Installazione di huggingface CLI[cite: 1]
RUN python3 -m pip install --no-cache-dir --break-system-packages -U \
    pip "huggingface_hub[cli]" hf_transfer

# Installazione globale di Pi Agent[cite: 1]
RUN npm install -g --unsafe-perm --ignore-scripts @earendil-works/pi-coding-agent

# 4070  172.19.16.1
# 5050  172.22.16.1

# Preconfigurazione di Git a livello di sistema (valida per root e agent_user)
RUN git config --system --add safe.directory '*' && \
    git config --system user.name "Pi Agent" && \
    git config --system user.email "pi-agent@local.dev"

COPY _include_docker/init.sh /init.sh

# abilito avvio scripts
RUN chmod +x /init.sh

# Imposta l'entrypoint
ENTRYPOINT ["/init.sh"]

# WORKDIR /scripts
WORKDIR /workspace
