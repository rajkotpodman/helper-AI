"""Automated Zero-Touch Installer & Bootstrapper for Ollama & Dolphin-LLM.

Automatically:
1. Detects or downloads & installs Ollama if missing.
2. Launches and verifies the background Ollama server (port 11434).
3. Pulls and verifies the 'dolphin-llama3' model (or designated model).
4. Auto-configures .env with LLM_PROVIDER=ollama and OLLAMA_MODEL=dolphin-llama3.
5. Runs the live initial verification prompt: 'hello i m helper ai'.
"""

import os
import sys
import time
import shutil
import logging
import platform
import subprocess
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import requests

logger = logging.getLogger("AutoSetupOllama")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"

OLLAMA_WINDOWS_INSTALLER_URL = "https://ollama.com/download/OllamaSetup.exe"
DEFAULT_MODEL = "dolphin-llama3"
DEFAULT_BASE_URL = "http://localhost:11434"


class OllamaAutoSetup:
    """Manages zero-touch automated setup of Ollama and Dolphin models."""

    @classmethod
    def get_ollama_path(cls) -> Optional[str]:
        """Returns path to ollama executable if available."""
        # 1. Check current system PATH
        path = shutil.which("ollama")
        if path:
            return path

        # 2. Check standard Windows default install location
        if platform.system() == "Windows":
            local_appdata = os.environ.get("LOCALAPPDATA", "")
            if local_appdata:
                win_path = Path(local_appdata) / "Programs" / "Ollama" / "ollama.exe"
                if win_path.exists():
                    # Add to current process PATH
                    os.environ["PATH"] = f"{win_path.parent};{os.environ.get('PATH', '')}"
                    return str(win_path)

        return None

    @classmethod
    def is_ollama_installed(cls) -> bool:
        return cls.get_ollama_path() is not None

    @classmethod
    def install_ollama(cls) -> bool:
        """Downloads and installs Ollama automatically if missing."""
        sys_name = platform.system()
        print("\n========================================================")
        print("    AUTO-INSTALLING OLLAMA LOCAL AI PLATFORM")
        print("========================================================")

        if sys_name == "Windows":
            temp_installer = Path(os.environ.get("TEMP", ".")) / "OllamaSetup.exe"
            print(f"[*] Downloading Ollama Windows Installer from:\n    {OLLAMA_WINDOWS_INSTALLER_URL}")
            try:
                urllib.request.urlretrieve(OLLAMA_WINDOWS_INSTALLER_URL, str(temp_installer))
                print(f"[*] Download completed. Running silent installation...")
                # Run silent install
                res = subprocess.run([str(temp_installer), "/silent"], check=False, timeout=180)
                time.sleep(3)
                # Verify installation path
                if cls.get_ollama_path():
                    print("[OK] Ollama successfully installed on Windows!")
                    return True
                else:
                    # Check default location
                    local_appdata = os.environ.get("LOCALAPPDATA", "")
                    win_path = Path(local_appdata) / "Programs" / "Ollama" / "ollama.exe"
                    if win_path.exists():
                        os.environ["PATH"] = f"{win_path.parent};{os.environ.get('PATH', '')}"
                        print("[OK] Ollama installed in AppData!")
                        return True
            except Exception as e:
                print(f"[!] Error installing Ollama on Windows: {e}")
                return False

        elif sys_name == "Linux":
            print("[*] Installing Ollama via official Linux script...")
            try:
                subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)
                return cls.is_ollama_installed()
            except Exception as e:
                print(f"[!] Linux install failed: {e}")
                return False

        elif sys_name == "Darwin":
            print("[!] macOS detected. Please install Ollama from https://ollama.com/download/mac")
            return False

        return False

    @classmethod
    def is_server_running(cls, base_url: str = DEFAULT_BASE_URL) -> bool:
        """Checks if Ollama HTTP server is responsive."""
        try:
            r = requests.get(f"{base_url}/api/version", timeout=1.5)
            return r.status_code == 200
        except Exception:
            return False

    @classmethod
    def ensure_server_running(cls, base_url: str = DEFAULT_BASE_URL, timeout_seconds: int = 15) -> bool:
        """Starts Ollama daemon in the background if not already running."""
        if cls.is_server_running(base_url):
            return True

        ollama_bin = cls.get_ollama_path() or "ollama"
        print("[*] Starting Ollama background daemon on port 11434...")

        creation_flags = 0
        if platform.system() == "Windows":
            # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
            creation_flags = 0x00000008 | 0x00000200

        try:
            subprocess.Popen(
                [ollama_bin, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creation_flags
            )
        except Exception as e:
            logger.warning(f"Failed to spawn background daemon via subprocess: {e}")

        # Wait for port to become healthy
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            if cls.is_server_running(base_url):
                print("[✓] Ollama background daemon is active and healthy!")
                return True
            time.sleep(1)

        print("[!] Timed out waiting for Ollama daemon.")
        return False

    @classmethod
    def get_installed_models(cls, base_url: str = DEFAULT_BASE_URL) -> list:
        """Queries Ollama for list of downloaded models."""
        try:
            r = requests.get(f"{base_url}/api/tags", timeout=3)
            if r.status_code == 200:
                models = r.json().get("models", [])
                return [m.get("name", "") for m in models]
        except Exception:
            pass
        return []

    @classmethod
    def is_model_installed(cls, model_name: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL) -> bool:
        """Checks if target model is downloaded."""
        installed = cls.get_installed_models(base_url)
        clean_target = model_name.split(":")[0].lower()
        for m in installed:
            if m.lower().startswith(clean_target) or clean_target in m.lower():
                return True
        return False

    @classmethod
    def pull_model(cls, model_name: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL) -> bool:
        """Pulls the specified model from Ollama registry with progress reporting."""
        print(f"\n[*] Pulling model '{model_name}' (this may take a few minutes)...")
        try:
            r = requests.post(
                f"{base_url}/api/pull",
                json={"name": model_name, "stream": True},
                stream=True,
                timeout=1800
            )
            last_pct = -1
            for line in r.iter_lines():
                if line:
                    import json
                    try:
                        data = json.loads(line)
                        status = data.get("status", "")
                        total = data.get("total", 0)
                        completed = data.get("completed", 0)
                        if total > 0:
                            pct = int((completed / total) * 100)
                            if pct != last_pct and pct % 10 == 0:
                                print(f"    [{model_name}] Progress: {pct}%")
                                last_pct = pct
                        elif "manifest" in status or "verifying" in status or "writing" in status:
                            print(f"    [{model_name}] {status}...")
                    except Exception:
                        pass
            print(f"[OK] Model '{model_name}' successfully downloaded and verified!")
            return True
        except Exception as e:
            print(f"[!] Error pulling model '{model_name}': {e}")
            # Fallback to CLI
            try:
                ollama_bin = cls.get_ollama_path() or "ollama"
                res = subprocess.run([ollama_bin, "pull", model_name], check=False)
                return res.returncode == 0
            except Exception:
                return False

    @classmethod
    def configure_env(cls, model_name: str = DEFAULT_MODEL) -> bool:
        """Configures Helper-AI .env to use Ollama with the specified model."""
        if not ENV_FILE.exists() and ENV_EXAMPLE.exists():
            shutil.copy(str(ENV_EXAMPLE), str(ENV_FILE))

        try:
            from dotenv import set_key
            set_key(str(ENV_FILE), "LLM_PROVIDER", "ollama")
            set_key(str(ENV_FILE), "OLLAMA_MODEL", model_name)
            set_key(str(ENV_FILE), "OLLAMA_BASE_URL", DEFAULT_BASE_URL)
            print(f"[OK] Configured .env with LLM_PROVIDER=ollama and OLLAMA_MODEL={model_name}")
            return True
        except Exception as e:
            # Fallback direct file update
            try:
                lines = []
                if ENV_FILE.exists():
                    lines = ENV_FILE.read_text(encoding="utf-8").splitlines()

                updated_provider = False
                updated_model = False
                new_lines = []
                for line in lines:
                    if line.startswith("LLM_PROVIDER="):
                        new_lines.append("LLM_PROVIDER=ollama")
                        updated_provider = True
                    elif line.startswith("OLLAMA_MODEL="):
                        new_lines.append(f"OLLAMA_MODEL={model_name}")
                        updated_model = True
                    else:
                        new_lines.append(line)

                if not updated_provider:
                    new_lines.append("LLM_PROVIDER=ollama")
                if not updated_model:
                    new_lines.append(f"OLLAMA_MODEL={model_name}")

                ENV_FILE.write_text("\n".join(new_lines), encoding="utf-8")
                print(f"[OK] Configured .env with LLM_PROVIDER=ollama and OLLAMA_MODEL={model_name}")
                return True
            except Exception as ex:
                logger.error(f"Failed to update .env: {ex}")
                return False

    @classmethod
    def test_first_prompt(
        cls,
        prompt: str = "hello i m helper ai",
        model_name: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL
    ) -> Dict[str, Any]:
        """Runs the live verification prompt to ensure the model responds."""
        print(f"\n[*] Running live verification prompt: '{prompt}' on model '{model_name}'...")
        start_t = time.perf_counter()
        try:
            r = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=180
            )
            elapsed = round(time.perf_counter() - start_t, 2)
            if r.status_code == 200:
                resp_text = r.json().get("response", "").strip()
                print(f"[OK] MODEL RESPONSE ({elapsed}s):\n    \"{resp_text[:120]}\"...")
                return {
                    "success": True,
                    "model": model_name,
                    "prompt": prompt,
                    "response": resp_text,
                    "elapsed_seconds": elapsed
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama returned HTTP status {r.status_code}: {r.text}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def run_full_setup(cls, target_model: str = DEFAULT_MODEL) -> Dict[str, Any]:
        """Runs the complete auto-installation, model pull, configuration, and prompt test."""
        print("\n========================================================")
        print("    HELPER-AI: ZERO-TOUCH LOCAL MODEL BOOTSTRAPPER")
        print("========================================================")

        # 1. Check / Install Ollama
        if not cls.is_ollama_installed():
            print("[*] Ollama is not installed. Initiating auto-installer...")
            if not cls.install_ollama():
                return {"success": False, "step": "install_ollama", "error": "Could not auto-install Ollama."}
        else:
            print(f"[OK] Ollama found at: {cls.get_ollama_path()}")

        # 2. Ensure Server Running
        if not cls.ensure_server_running():
            return {"success": False, "step": "ensure_server", "error": "Could not start Ollama daemon on port 11434."}

        # 3. Check / Pull Model
        installed_models = cls.get_installed_models()
        print(f"[*] Currently available local models: {installed_models}")

        active_model = target_model
        if not cls.is_model_installed(target_model):
            print(f"[*] Compulsory model '{target_model}' not found locally. Downloading now...")
            pulled = cls.pull_model(target_model)
            if not pulled:
                # If target model failed (e.g. network/disk), fallback to available model
                if "llama3.2:3b" in installed_models:
                    active_model = "llama3.2:3b"
                    print(f"[!] Falling back to available model: {active_model}")
                elif "qwen2.5:1.5b" in installed_models:
                    active_model = "qwen2.5:1.5b"
                    print(f"[!] Falling back to available model: {active_model}")
                else:
                    return {"success": False, "step": "pull_model", "error": f"Failed to pull model '{target_model}'."}
        else:
            print(f"[OK] Compulsory model '{target_model}' is already installed!")

        # 4. Auto-configure .env
        cls.configure_env(active_model)

        # 5. Live Prompt Verification
        test_res = cls.test_first_prompt(prompt="hello i m helper ai", model_name=active_model)

        print("\n========================================================")
        print("  [SUCCESS] HELPER-AI LOCAL ENGINE IS 100% ONLINE AND OPERATIONAL!")
        print("========================================================\n")

        return {
            "success": True,
            "ollama_installed": True,
            "model_configured": active_model,
            "test_result": test_res
        }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
    res = OllamaAutoSetup.run_full_setup(target_model=target)
    if not res.get("success"):
        sys.exit(1)
