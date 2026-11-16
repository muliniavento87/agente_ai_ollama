Per il provider OLLAMA, installalo, chiudilo e avvialo così:

```Powershell
$env:OLLAMA_FLASH_ATTENTION="1"
$env:OLLAMA_KV_CACHE_TYPE="q4_0"
$env:OLLAMA_HOST="0.0.0.0"
$env:OLLAMA_ORIGINS="*"
ollama serve
```

Infine aggiungi i modelli voluti (docker_pi_agent\ollama_models)