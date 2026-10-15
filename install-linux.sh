#!/usr/bin/env bash
# ==============================================================================
# Helper-AI: One-Click Linux Setup & Installer
# Works on: Ubuntu, Debian, Fedora, Arch Linux, CentOS, RHEL, openSUSE
# ==============================================================================
set -e

echo "========================================================"
echo "    HELPER-AI: AUTONOMOUS PC & INTERNET AGENT (LINUX)   "
echo "========================================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "[*] Detecting Linux distribution and package manager..."
if command -v apt-get &> /dev/null; then
    echo "[*] Debian/Ubuntu detected. Installing system prerequisites..."
    sudo apt-get update -qq || true
    sudo apt-get install -y python3 python3-pip python3-venv python3-tk scrot xvfb libx11-dev xclip curl git || true
elif command -v dnf &> /dev/null; then
    echo "[*] Fedora/RHEL detected. Installing system prerequisites..."
    sudo dnf install -y python3 python3-pip python3-tkinter xorg-x11-server-Xvfb scrot xclip curl git || true
elif command -v pacman &> /dev/null; then
    echo "[*] Arch Linux detected. Installing system prerequisites..."
    sudo pacman -Sy --noconfirm python python-pip tk xorg-server-xvfb scrot xclip curl git || true
fi

echo "[*] Verifying Python 3.10+..."
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 not found. Please install Python 3.10+ from your package manager."
    exit 1
fi

echo "[*] Running Universal Helper-AI installer..."
python3 install.py

echo ""
echo "[*] Setting execution permissions..."
chmod +x app.py helper.py start.bat || true

echo "========================================================"
echo "  Helper-AI Linux Setup Successfully Completed!         "
echo "  To run: python3 app.py                                "
echo "  Or type 'helper-ai' in terminal                       "
echo "========================================================"
