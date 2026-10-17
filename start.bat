@echo off
title Helper-AI Launcher
color 0b
echo ========================================================
echo         HELPER-AI: AUTONOMOUS PC & INTERNET AGENT
echo ========================================================
echo.
echo [*] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not found on your system!
    echo     Please install Python 3.10+ from python.org and add to PATH.
    pause
    exit /b 1
)

echo [*] Verifying dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check

echo [*] Ensuring Ollama & Local AI models are ready...
python core/auto_setup_ollama.py dolphin-llama3


echo.
echo [*] Starting Helper-AI Web Dashboard...
echo [*] Your browser will open automatically at http://localhost:8000
echo.
python app.py
pause
