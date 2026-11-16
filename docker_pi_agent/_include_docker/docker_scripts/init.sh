#!/bin/bash

# ---------- Init ["Pi Agent"] configurazione ----------
if [ -d "/etc/.pi/agent/npm" ]; then
    # cartella esiste
    echo "Estensioni Pi Agent già installate."
else
    # installo estensioni
    chmod +x /scripts/sh_include_init/init_pi_config.sh
    /scripts/sh_include_init/init_pi_config.sh
fi

# ---------- Init ["Pi Agent"] mattpocock skills ----------
# default => true
DOWNLOAD_MATTPOCOCK_SKILLS=false
if [ -d "/etc/.pi/agent/skills/mattpocock" ]; then
    # cartella esiste, è richiesto il FORCE del ridownload?
    if [[ "$FORCE_DOWNLOAD_MATTPOCOCK_SKILLS" == "true" ]]; then
        DOWNLOAD_MATTPOCOCK_SKILLS=true
        # forzo il redownload, rimuovo la cartella esistente
        rm -rf /etc/.pi/agent/skills/mattpocock
    fi
else
    DOWNLOAD_MATTPOCOCK_SKILLS=true
fi
if [[ "$DOWNLOAD_MATTPOCOCK_SKILLS" == "true" ]]; then
    # FIRST TIME => Init ["Pi Agent"] mattpocock skills
    chmod +x /scripts/sh_include_init/init_pi_mattpocock_skills.sh
    /scripts/sh_include_init/init_pi_mattpocock_skills.sh
fi

# ---------- Esegue il comando principale passato al container e apre la bash ----------
exec "${@:-bash}"
