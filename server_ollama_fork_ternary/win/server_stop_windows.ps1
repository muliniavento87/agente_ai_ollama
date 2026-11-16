# Interrompi lo script in caso di errori critici di PowerShell
$ErrorActionPreference = "Stop"

# Spostati nella cartella root del progetto (2 livelli sopra rispetto a run_docker/win/)
$ScriptDir = $PSScriptRoot
Set-Location "$ScriptDir"

Write-Host "==> Arresto dei servizi server..." -ForegroundColor Yellow
wsl docker compose -f docker-compose.win-server.yml down
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Servizi server arrestati con successo!" -ForegroundColor Green