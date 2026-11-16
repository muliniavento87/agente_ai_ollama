# Interrompi lo script in caso di errori critici di PowerShell
$ErrorActionPreference = "Stop"

# Spostati nella cartella root del progetto (2 livelli sopra rispetto a run_docker/win/)
$ScriptDir = $PSScriptRoot
Set-Location "$ScriptDir"

Write-Host "==> [1/2] Build e avvio dei servizi server..." -ForegroundColor Cyan
wsl docker compose -f docker-compose.win-server.yml up -d --build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> [2/2] Avvio dello streaming dei log per 'llama-server' (CTRL+C per uscire)..." -ForegroundColor Cyan
wsl docker compose -f docker-compose.win-server.yml logs -f llama-server