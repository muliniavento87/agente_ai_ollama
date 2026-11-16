#!/bin/bash
set -e

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
pi install https://github.com/gsanhueza/pi-token-speed && \
# pi install npm:pi-sandbox && \
# pi install npm:pi-mcp-extension && \
pi install npm:pi-atelier
