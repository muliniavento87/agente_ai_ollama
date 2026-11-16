# Run veloce
La prima volta deve scaricare circa 6gb di modello, quindi è lentissimo, aspetta.

- mac
  - se errore porta 8080 occupata (lsof -i :8080; kill -9 <pid>)
```bash
./mac/server_run_mac.sh
```
- windows
```Powershell
./win/server_run_windows.ps1
./win/server_stop_windows.ps1
```


# Installazione e run (Mac)
La prima volta deve scaricare circa 6gb di modello, quindi è lentissimo, aspetta.

- test e chat  http://localhost:8080/
```bash
./mac/server_run_mac.sh
```
- se non funzionasse:
```bash
mkdir -p models
curl -fL -C - -o models/Ternary-Bonsai-2-27B-PTQ1_0.gguf \
"https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf/resolve/main/Ternary-Bonsai-2-27B-PTQ1_0.gguf"
```
## Uninstall
PER DISINSTALLARLO completamente dall' HOST => Cancella fisicamente la cartella dei binari (il server) e il modello .gguf scaricato
```bash
rm -rf ~/.local/llama-prism
rm -f ./models/Ternary-Bonsai-2-27B-PTQ1_0.gguf
```


# Installazione e run (Windows)
La prima volta deve scaricare circa 6gb di modello, quindi è lentissimo, aspetta.

## Config (esposizione in rete)
- da admin powershell apri il passaggio dal firewall con questo comando (altrimenti Windows da Mac non sarà raggiungibile)
```
New-NetFirewallRule -Name "Allow_Llama_Server" -DisplayName "Consenti Llama Server (Porta 8080)" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Enabled TrueTrue
```
- per rendere raggiungibile il server in rete, da PowerShell come amministratore:
```
$ip = (wsl hostname -I).Split(' ')[0]   # IP della distro                          
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8080 connectaddress=$ip connectport=8080
```

## Run
- test e chat  http://localhost:8080/
```Powershell
./win/server_run_windows.ps1
```

## Stop
```Powershell
./win/server_stop_windows.ps1
```

# run Curl
```bash
curl -i http://host.docker.internal:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Ternary-Bonsai-2-27B-PTQ1_0",
    "messages": [{"role": "user", "content": "Rispondi solo con la parola OK."}],
    "max_tokens": 32
  }'
```