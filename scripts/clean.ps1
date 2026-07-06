# clean.ps1
# Script to clean up caching and temp folders

$projectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Cleaning up cached directories..." -ForegroundColor Yellow

$foldersToDelete = @(
    "$projectRoot\backend\__pycache__",
    "$projectRoot\backend\venv",
    "$projectRoot\frontend\.next",
    "$projectRoot\frontend\node_modules"
)

foreach ($folder in $foldersToDelete) {
    if (Test-Path $folder) {
        Write-Host "Removing $folder..."
        Remove-Item -Path $folder -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Cleanup completed successfully!" -ForegroundColor Green
