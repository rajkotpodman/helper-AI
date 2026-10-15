@echo off
title Helper-AI Windows Installer & Setup
color 0b
echo ========================================================
echo         HELPER-AI: WINDOWS SETUP & INSTALLER
echo ========================================================
echo.

cd /d "%~dp0"

echo [*] Checking Python 3.10+ installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed or not in your system PATH!
    echo     Please download and install Python 3.10+ from https://www.python.org/downloads/
    echo     Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [*] Running Python Universal Installer & Shortcut Generator...
python install.py

echo.
echo [*] Testing server startup and module integrity...
python -c "import app, helper, core.agent; print('[✓] All modules verified cleanly!')"

echo.
echo ========================================================
echo   Helper-AI is ready!
echo   Double-click 'start.bat' or use the Desktop shortcut.
echo ========================================================
echo.
pause
