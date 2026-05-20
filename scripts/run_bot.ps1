$ErrorActionPreference = "Continue"

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$logDir = Join-Path $root "logs"
$logFile = Join-Path $logDir "bot.log"

New-Item -ItemType Directory -Force $logDir | Out-Null
Set-Location $root
$env:PYTHONUNBUFFERED = "1"

& $python -m company_bot >> $logFile 2>&1
