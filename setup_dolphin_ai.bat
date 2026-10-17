@echo off
title Helper-AI: 1-Click Dolphin-LLM & Local AI Auto-Installer
color 0b
echo ========================================================
echo   HELPER-AI: 1-CLICK OLLAMA & DOLPHIN-LLAMA3 SETUP
echo ========================================================
echo.
echo [*] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed!
    echo     Please install Python 3.10+ from python.org and add to PATH.
    pause
    exit /b 1
)

echo [*] Installing required python libraries...
pip install -r requirements.txt --quiet --disable-pip-version-check

echo.
echo [*] Launching automated zero-touch setup...
python core/auto_setup_ollama.py dolphin-llama3

if %errorlevel% neq 0 (
    echo.
    echo [!] Setup encountered a warning. Launching Helper-AI anyway...
)

echo.
echo [*] Starting Helper-AI Web Dashboard...
echo [*] Opening http://localhost:8000 in your browser...
echo.
start "" "http://localhost:8000"
python app.py
pause
