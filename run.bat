@echo off
REM Plex TV Show Renamer - Windows Launcher
REM Launches the renamer with proper Python interpreter

setlocal enabledelayedexpansion

REM Get the directory this batch file is in
for %%I in ("%~dp0.") do set SCRIPT_DIR=%%~fI

echo.
echo ========================================
echo   Plex TV Show Renamer
echo ========================================
echo.

REM Try to find Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python "%SCRIPT_DIR%\plex_renamer.py"
) else (
    echo Error: Python not found in PATH
    echo.
    echo Please install Python 3.7+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

pause
