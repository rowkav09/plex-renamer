# Plex TV Show Renamer - PowerShell Launcher

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RenamerScript = Join-Path $ScriptDir "plex_renamer.py"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Plex TV Show Renamer" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Python is available
try {
    $PythonVersion = python --version 2>&1
    Write-Host "Found: $PythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Error: Python not found!" -ForegroundColor Red
    Write-Host "`nPlease install Python 3.7+ from:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "`nMake sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Read-Host "`nPress Enter to exit"
    exit 1
}

# Run the renamer
Write-Host "`nLaunching Plex Renamer...`n" -ForegroundColor Cyan
python $RenamerScript

Write-Host "`nDone." -ForegroundColor Green
