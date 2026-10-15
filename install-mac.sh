#!/usr/bin/env bash
# ==============================================================================
# Helper-AI: One-Click macOS Setup & Installer
# Supports: macOS (Intel x86_64 and Apple Silicon M1/M2/M3/M4)
# ==============================================================================
set -e

echo "========================================================"
echo "    HELPER-AI: AUTONOMOUS PC & INTERNET AGENT (MACOS)   "
echo "========================================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "[*] Checking for Homebrew..."
if command -v brew &> /dev/null; then
    echo "[*] Homebrew found. Verifying Python 3..."
    if ! command -v python3 &> /dev/null; then
        echo "[*] Installing Python via Homebrew..."
        brew install python
    fi
else
    echo "[!] Homebrew not detected. Ensuring system Python 3 is available..."
fi

echo "[*] Verifying Python installation..."
python3 --version

echo "[*] Running Universal Installer..."
python3 install.py

echo ""
echo "[*] Setting execution permissions..."
chmod +x app.py helper.py install.py launch_helper_ai.command 2>/dev/null || true

echo "========================================================"
echo "  Helper-AI macOS Setup Successfully Completed!         "
echo "  To launch: double click 'Helper-AI.command' on Desktop"
echo "  Or run: python3 app.py                                "
echo "========================================================"
