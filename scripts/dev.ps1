# dev.ps1
# Script to run both Backend and Frontend locally

$projectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Starting Backend..." -ForegroundColor Green
$backendProcess = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\backend'; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload" -PassThru

Write-Host "Starting Frontend..." -ForegroundColor Cyan
Set-Location -Path "$projectRoot\frontend"
npm run dev

# When user closes the frontend, close the backend too
if ($backendProcess -and !$backendProcess.HasExited) {
    Stop-Process -Id $backendProcess.Id -Force
}
