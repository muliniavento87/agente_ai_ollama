## Run veloce

```Powershell
$env:OLLAMA_FLASH_ATTENTION="1"
$env:OLLAMA_KV_CACHE_TYPE="q4_0"
$env:OLLAMA_HOST="0.0.0.0"
$env:OLLAMA_ORIGINS="*"
ollama serve
```

```Powershell
wsl docker compose up -d --build;
wsl docker exec -it pi-agent-dev bash

pi --no-session

wsl docker compose down
```

```Powershell
wsl docker compose down;
wsl docker compose up -d --build;
wsl docker exec -it pi-agent-dev bash
```

## pipeline
```bash
cd p;
python3 loop_prompt.py
```
