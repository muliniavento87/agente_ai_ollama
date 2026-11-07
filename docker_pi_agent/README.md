
# Ollama
- LFM 2.5
    - https://ollama.com/richardyoung/lfm2.5-24b-a2b:Q4_K_M
        - ollama run richardyoung/lfm2.5-24b-a2b:Q4_K_M
    - estensione browser per usare Ollama graficamente
        - Page Assist

## Mac
- avvia ollama (Mac) con le configurazioni ottimali
```bash
OLLAMA_FLASH_ATTENTION="1";
OLLAMA_KV_CACHE_TYPE="q4_0";
OLLAMA_HOST="0.0.0.0";
OLLAMA_ORIGINS="*";
ollama serve
```

## Windows
- avvia ollama (Windows) con le configurazioni ottimali
```Powershell
$env:OLLAMA_FLASH_ATTENTION="1"
$env:OLLAMA_KV_CACHE_TYPE="q4_0"
$env:OLLAMA_HOST="0.0.0.0"
$env:OLLAMA_ORIGINS="*"
ollama serve
```
- file variante del modello  "lfm2.5-24b-a2b:Q4_K_M" con la configurazione voluta
```Modelfile
FROM richardyoung/lfm2.5-24b-a2b:Q4_K_M
PARAMETER num_ctx 32768
PARAMETER num_predict 32768
```
- crea variante modello "lfm2.5-24b-a2b:Q4_K_M"
```Powershell
ollama create lfm2.5-32k -f Modelfile
```
- avvio
```
ollama run lfm2.5-32k
```

# Container
## Configurazione
Su Windows identifica l'indirizzo di Ollama visto dal container:
- wsl
```
ip route show default | awk '{print $3}'
```
- recupera l'IP che ti ha restituito il comando e mettilo in "Dockerfile" (in fondo al file) in questo punto:
    - "baseUrl":"http://172.19.16.1 ...
- se serve sblocca la porta sul firewall
```
New-NetFirewallRule -DisplayName "Ollama Docker WSL" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434
```
## Avvia il container
```
wsl docker compose up -d --build
wsl docker exec -it pi-agent-dev bash
pi --no-session
wsl docker compose down
```

# Pi Agent
## Estensioni
- mostra token al secondo
```
pi install https://github.com/gsanhueza/pi-token-speed
```