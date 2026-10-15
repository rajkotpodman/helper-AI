#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# Helper-AI: One-Click Android Setup & Installer (via Termux)
# Enables standalone portable execution on any Android device!
# ==============================================================================
set -e

echo "========================================================"
echo "    HELPER-AI: AUTONOMOUS AGENT FOR ANDROID (TERMUX)    "
echo "========================================================"
echo ""

echo "[*] Updating Termux packages..."
pkg update -y || true

echo "[*] Installing build prerequisites and Python 3..."
pkg install -y python git clang libxml2 libxslt libjpeg-turbo libpng rust binutils curl || true

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "[*] Upgrading pip and wheel..."
pip install --upgrade pip setuptools wheel --quiet

echo "[*] Installing Python dependencies (pure-python optimized for mobile)..."
# Exclude GUI-only dependencies on headless Android Termux
grep -v -E "pyautogui|PyAutoGUI|scrot|xvfb|playwright" requirements.txt > termux_requirements.txt || cp requirements.txt termux_requirements.txt
pip install -r termux_requirements.txt --disable-pip-version-check

echo "[*] Creating Android launcher shortcut 'helper-ai'..."
mkdir -p "$PREFIX/bin"
cat << 'EOF' > "$PREFIX/bin/helper-ai"
#!/data/data/com.termux/files/usr/bin/bash
DIR="$(dirname "$(realpath "$0")")"
PROJECT_DIR="$HOME/helper-AI"
if [ ! -d "$PROJECT_DIR" ]; then
    PROJECT_DIR="$(pwd)"
fi
cd "$PROJECT_DIR"
echo "[*] Starting Helper-AI on Android..."
echo "[*] Open http://localhost:8000 in Chrome / Brave on your phone!"
python3 app.py
EOF
chmod +x "$PREFIX/bin/helper-ai"

echo ""
echo "========================================================"
echo "  Helper-AI Android Installation Succeeded!             "
echo "  Run 'helper-ai' anytime in Termux.                    "
echo "  Dashboard: http://localhost:8000 in your mobile browser"
echo "========================================================"
