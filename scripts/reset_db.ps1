# reset_db.ps1
# Script to reset database and seed initial data

$projectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Resetting Database..." -ForegroundColor Cyan
Set-Location -Path "$projectRoot\backend"

if (Test-Path ".\venv\Scripts\Activate.ps1") {
    . ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "Virtual environment not found! Please setup environment first." -ForegroundColor Red
    exit 1
}

if (Test-Path "reset_db.py") {
    python reset_db.py
}
if (Test-Path "seed_subjects.py") {
    python seed_subjects.py
}
if (Test-Path "seed_data.py") {
    python seed_data.py
}

Write-Host "Database reset and seed completed." -ForegroundColor Green
