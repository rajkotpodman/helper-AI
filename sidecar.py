"""Helper-AI: Hands-free Voice Agent & Desktop Sidecar Companion.

Runs as a lightweight, background Windows Desktop sidecar:
1. Listens for global hotkey (Default: Ctrl+Shift+Space) to summon the voice agent.
2. Captures user speech or input, sends to Helper-AI Voice Engine.
3. Speaks results aloud through PC speakers via Edge-TTS / SAPI5 fallback.
4. Seamlessly bridges PC desktop control with autonomous agent workflows.
"""

import os
import sys
import time
import json
import ctypes
import logging
import argparse
import threading
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Sidecar] %(message)s"
)
logger = logging.getLogger("VoiceSidecar")

SERVER_URL = os.getenv("HELPER_SERVER_URL", "http://127.0.0.1:8000")
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "en-US-AriaNeural")

# Win32 Constants for Hotkey
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
VK_SPACE = 0x20
VK_H = 0x48
HOTKEY_ID = 101


class DesktopVoiceSidecar:
    """Windows Desktop Sidecar for Hands-free Voice Interaction with Helper-AI."""

    def __init__(self, server_url: str = SERVER_URL, voice: str = DEFAULT_VOICE):
        self.server_url = server_url.rstrip("/")
        self.voice = voice
        self._running = False
        self._user32 = ctypes.windll.user32

    def check_server(self) -> bool:
        """Verifies if the Helper-AI backend server is reachable."""
        try:
            r = requests.get(f"{self.server_url}/api/voice/voices", timeout=2.5)
            return r.status_code == 200
        except Exception:
            return False

    def notify_windows(self, title: str, message: str):
        """Displays a lightweight PowerShell Windows balloon/toast notification."""
        try:
            ps_cmd = f"""
            Add-Type -AssemblyName System.Windows.Forms
            $notify = New-Object System.Windows.Forms.NotifyIcon
            $notify.Icon = [System.Drawing.SystemIcons]::Information
            $notify.Visible = $true
            $notify.ShowBalloonTip(4000, '{title.replace("'", "''")}', '{message.replace("'", "''")}', [System.Windows.Forms.ToolTipIcon]::Info)
            Start-Sleep -Milliseconds 200
            $notify.Dispose()
            """
            import subprocess
            subprocess.Popen(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            logger.debug(f"Notification error: {e}")

    def speak(self, text: str, voice: Optional[str] = None):
        """Speaks text aloud through host PC speakers via VoiceEngine."""
        from core.voice_engine import VoiceEngine
        target_voice = voice or self.voice
        logger.info(f"Speaking: '{text}' ({target_voice})")
        VoiceEngine.speak_on_pc(text, voice=target_voice)

    def dispatch_voice_command(self, text: str) -> dict:
        """Sends transcript command to Helper-AI backend dispatch endpoint."""
        logger.info(f"Dispatching command: '{text}'")
        try:
            resp = requests.post(
                f"{self.server_url}/api/voice/dispatch",
                json={
                    "transcript": text,
                    "voice": self.voice,
                    "speak_on_pc": True
                },
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                reply = data.get("reply", "Task finished.")
                self.notify_windows("Helper-AI Voice Response", reply)
                return data
            else:
                err_msg = f"Server returned error code {resp.status_code}"
                self.speak(err_msg)
                return {"success": False, "error": err_msg}
        except Exception as e:
            logger.error(f"Failed to reach Helper-AI backend: {e}")
            self.speak("Could not connect to Helper-AI backend. Please ensure the server is running on port 8000.")
            return {"success": False, "error": str(e)}

    def prompt_and_execute(self):
        """Interactive audio or text dialog triggered by hotkey."""
        logger.info(">>> Voice Agent Activated via Hotkey! <<<")
        self.notify_windows("Helper-AI Voice Sidecar", "Listening... Type or speak your command.")
        
        # Open small input box or interactive prompt
        try:
            import tkinter as tk
            from tkinter import simpledialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            user_input = simpledialog.askstring(
                "Helper-AI Hands-Free Voice Agent",
                "Spoken Command / Goal Prompt:\n(e.g., 'What is my CPU usage?', 'Open GitHub', 'Search web for 2026 AI')",
                parent=root
            )
            root.destroy()

            if user_input and user_input.strip():
                self.dispatch_voice_command(user_input.strip())
        except Exception as e:
            logger.error(f"Dialog prompt error: {e}")

    def run_hotkey_listener(self):
        """Registers global Windows hotkey Ctrl+Shift+Space and listens in event loop."""
        # Hotkey: MOD_CONTROL (0x2) + MOD_SHIFT (0x4) + VK_SPACE (0x20)
        fs_modifiers = MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT
        vk = VK_SPACE

        if not self._user32.RegisterHotKey(None, HOTKEY_ID, fs_modifiers, vk):
            logger.warning("Could not register Ctrl+Shift+Space hotkey. Trying Alt+Shift+H...")
            fs_modifiers = MOD_ALT | MOD_SHIFT | MOD_NOREPEAT
            vk = VK_H
            if not self._user32.RegisterHotKey(None, HOTKEY_ID, fs_modifiers, vk):
                logger.error("Failed to register global hotkey. Sidecar will run in CLI mode.")
                return False

        logger.info("==================================================")
        logger.info("  Helper-AI Hands-Free Voice Sidecar is ACTIVE!  ")
        logger.info("  Press [Ctrl + Shift + Space] anywhere in Windows")
        logger.info("  to summon the voice assistant immediately.     ")
        logger.info("==================================================")
        self.notify_windows(
            "Helper-AI Voice Sidecar Active",
            "Press [Ctrl+Shift+Space] anytime to summon hands-free assistant!"
        )

        self._running = True
        try:
            msg = ctypes.wintypes.MSG()
            while self._running:
                # Wait for Windows message
                if self._user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                    if msg.message == 0x0312:  # WM_HOTKEY
                        if msg.wParam == HOTKEY_ID:
                            threading.Thread(target=self.prompt_and_execute, daemon=True).start()
                    self._user32.TranslateMessage(ctypes.byref(msg))
                    self._user32.DispatchMessageW(ctypes.byref(msg))
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down Voice Sidecar...")
        finally:
            self._user32.UnregisterHotKey(None, HOTKEY_ID)
            self._running = False
        return True


def main():
    parser = argparse.ArgumentParser(description="Helper-AI Hands-free Voice Agent & Desktop Sidecar")
    parser.add_argument("--hotkey", action="store_true", default=True, help="Run background global hotkey listener (Ctrl+Shift+Space)")
    parser.add_argument("--speak", type=str, default=None, help="Speak a text message immediately")
    parser.add_argument("--command", type=str, default=None, help="Execute a voice command immediately")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Neural voice identifier")
    parser.add_argument("--server", type=str, default=SERVER_URL, help="Helper-AI backend URL")

    args = parser.parse_args()
    sidecar = DesktopVoiceSidecar(server_url=args.server, voice=args.voice)

    if args.speak:
        sidecar.speak(args.speak, voice=args.voice)
        return

    if args.command:
        res = sidecar.dispatch_voice_command(args.command)
        print(json.dumps(res, indent=2))
        return

    if args.hotkey:
        sidecar.run_hotkey_listener()


if __name__ == "__main__":
    main()
