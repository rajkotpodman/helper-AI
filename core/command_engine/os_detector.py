"""Cross-Platform Operating System and Environment Detection Engine.

Provides deep introspection into the host operating system, active kernel,
available shells, privilege levels, and installed package managers.
"""

import os
import sys
import shutil
import platform
import subprocess
from typing import Dict, Any, List, Optional


class OSDetector:
    """Introspects host operating system, environment, and shell capabilities."""

    @staticmethod
    def detect_os() -> Dict[str, Any]:
        """Identifies OS family, distribution, kernel version, and architecture."""
        system_name = platform.system().lower()
        release = platform.release()
        version = platform.version()
        arch = platform.machine()

        os_family = "unknown"
        distro = ""

        if system_name == "windows":
            os_family = "windows"
            distro = f"Windows {release}"
        elif system_name == "darwin":
            os_family = "macos"
            distro = f"macOS {platform.mac_ver()[0] or release}"
        elif system_name == "linux":
            os_family = "linux"
            # Detect WSL
            if "microsoft" in release.lower() or "wsl" in release.lower():
                os_family = "wsl"
            # Try reading /etc/os-release for distro name
            distro = OSDetector._detect_linux_distro()
        elif "bsd" in system_name:
            os_family = "bsd"
            distro = system_name.capitalize()

        return {
            "family": os_family,
            "system": system_name,
            "distro": distro or system_name.capitalize(),
            "release": release,
            "version": version,
            "architecture": arch,
            "python_version": platform.python_version()
        }

    @staticmethod
    def _detect_linux_distro() -> str:
        """Reads /etc/os-release on Linux systems if present."""
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            return line.split("=", 1)[1].strip().strip('"')
                        if line.startswith("NAME="):
                            return line.split("=", 1)[1].strip().strip('"')
        except Exception:
            pass
        return "Linux"

    @staticmethod
    def detect_available_shells() -> Dict[str, str]:
        """Detects all available terminal shells on the system and their binary paths."""
        candidate_shells = [
            "powershell.exe",
            "pwsh",
            "cmd.exe",
            "bash",
            "zsh",
            "sh",
            "fish",
            "dash"
        ]
        available = {}
        for sh in candidate_shells:
            path = shutil.which(sh)
            if path:
                available[sh] = path
        return available

    @classmethod
    def get_preferred_shell(cls) -> Dict[str, str]:
        """Determines the primary/most capable shell for the host environment."""
        os_info = cls.detect_os()
        available = cls.detect_available_shells()

        if os_info["family"] in ["windows"]:
            if "powershell.exe" in available:
                return {"shell": "powershell", "binary": available["powershell.exe"], "type": "powershell"}
            if "pwsh" in available:
                return {"shell": "pwsh", "binary": available["pwsh"], "type": "powershell"}
            if "cmd.exe" in available:
                return {"shell": "cmd", "binary": available["cmd.exe"], "type": "cmd"}
            return {"shell": "cmd", "binary": "cmd.exe", "type": "cmd"}
        else:
            if "bash" in available:
                return {"shell": "bash", "binary": available["bash"], "type": "posix"}
            if "zsh" in available:
                return {"shell": "zsh", "binary": available["zsh"], "type": "posix"}
            if "sh" in available:
                return {"shell": "sh", "binary": available["sh"], "type": "posix"}
            return {"shell": "sh", "binary": "/bin/sh", "type": "posix"}

    @staticmethod
    def detect_package_managers() -> Dict[str, Optional[str]]:
        """Scans for available package managers across all OS ecosystems."""
        managers = [
            "winget", "choco", "scoop",               # Windows
            "apt-get", "apt", "dnf", "yum", "pacman", # Linux
            "apk", "zypper", "snap", "flatpak",        # Linux alternate
            "brew",                                    # macOS / Linux
            "pip", "pip3", "npm", "yarn", "pnpm",     # Language managers
            "cargo", "go", "gem", "dotnet"             # Compilers / Run-times
        ]
        found = {}
        for m in managers:
            loc = shutil.which(m)
            if loc:
                found[m] = loc
        return found

    @staticmethod
    def is_elevated() -> bool:
        """Checks if current process has Administrator or root privileges."""
        try:
            if os.name == "nt":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False

    @classmethod
    def get_system_context(cls) -> Dict[str, Any]:
        """Generates a complete system context payload for agent planning."""
        os_info = cls.detect_os()
        preferred_shell = cls.get_preferred_shell()
        available_shells = cls.detect_available_shells()
        pkg_managers = cls.detect_package_managers()
        elevated = cls.is_elevated()

        return {
            "os": os_info,
            "preferred_shell": preferred_shell,
            "available_shells": list(available_shells.keys()),
            "package_managers": list(pkg_managers.keys()),
            "is_elevated": elevated,
            "cwd": os.getcwd()
        }
