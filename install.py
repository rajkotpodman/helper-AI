#!/usr/bin/env python3
"""
Helper-AI: Universal Cross-Platform Setup & Installer
Supports: Windows, macOS, Linux, and Android (Termux).
"""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def print_header(text: str):
    print("\n" + "=" * 60)
    print(f"   {text}")
    print("=" * 60)

def print_step(text: str):
    print(f"[*] {text}")

def print_success(text: str):
    print(f"[✓] {text}")

def print_error(text: str):
    print(f"[!] {text}")

def detect_os() -> str:
    if "com.termux" in os.environ.get("PREFIX", "") or "ANDROID_ROOT" in os.environ:
        return "android"
    system = platform.system().lower()
    if system.startswith("win"):
        return "windows"
    elif system.startswith("darwin"):
        return "macos"
    elif system.startswith("linux"):
        return "linux"
    return "unknown"

def check_python_version():
    print_step(f"Detecting Python version: {platform.python_version()} on {platform.system()}...")
    if sys.version_info < (3, 10):
        print_error("Python 3.10 or higher is required. Please upgrade your Python installation.")
        sys.exit(1)
    print_success(f"Python {platform.python_version()} verified.")

def install_dependencies(root_dir: Path):
    req_file = root_dir / "requirements.txt"
    if not req_file.exists():
        print_error(f"requirements.txt not found in {root_dir}")
        return False

    print_step("Installing & verifying required Python packages...")
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"]
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print_step(f"Pip upgrade note: {e}")

    install_cmd = [sys.executable, "-m", "pip", "install", "-r", str(req_file), "--disable-pip-version-check"]
    try:
        res = subprocess.run(install_cmd, check=True)
        print_success("All core dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Dependency installation encountered an issue: {e}")
        return False

def setup_environment(root_dir: Path):
    env_file = root_dir / ".env"
    env_example = root_dir / ".env.example"
    if not env_file.exists() and env_example.exists():
        print_step("Creating .env from .env.example...")
        shutil.copy(env_example, env_file)
        print_success(".env initialized. Add your API keys if needed (or use offline Ollama / Rule Engine).")
    elif env_file.exists():
        print_success("Existing .env configuration preserved.")

def create_shortcuts(root_dir: Path, target_os: str):
    print_step(f"Creating launchers for {target_os.capitalize()}...")
    
    if target_os == "windows":
        run_bat = root_dir / "run.bat"
        if not run_bat.exists():
            with open(run_bat, "w") as f:
                f.write("@echo off\ncall start.bat\n")
        print_success(f"Windows batch launcher ready: {run_bat}")
        
        # Create Desktop Shortcut via VBScript
        try:
            desktop = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
            if desktop.exists():
                vbs_script = root_dir / "scratch" / "create_shortcut.vbs"
                vbs_script.parent.mkdir(parents=True, exist_ok=True)
                shortcut_path = desktop / "Helper-AI.lnk"
                target_path = root_dir / "start.bat"
                with open(vbs_script, "w") as f:
                    f.write(f'Set oWS = WScript.CreateObject("WScript.Shell")\n')
                    f.write(f'sLinkFile = "{shortcut_path}"\n')
                    f.write(f'Set oLink = oWS.CreateShortcut(sLinkFile)\n')
                    f.write(f'oLink.TargetPath = "{target_path}"\n')
                    f.write(f'oLink.WorkingDirectory = "{root_dir}"\n')
                    f.write(f'oLink.Description = "Helper-AI Autonomous PC & Internet Agent"\n')
                    f.write(f'oLink.Save\n')
                subprocess.run(["cscript", "//nologo", str(vbs_script)], check=False)
                if shortcut_path.exists():
                    print_success(f"Desktop shortcut created: {shortcut_path}")
        except Exception as e:
            print_step(f"Note on shortcut creation: {e}")

    elif target_os == "macos":
        launcher_file = root_dir / "launch_helper_ai.command"
        with open(launcher_file, "w") as f:
            f.write(f"#!/usr/bin/env bash\ncd '{root_dir}'\npython3 app.py\n")
        launcher_file.chmod(0o755)
        print_success(f"macOS clickable launcher created: {launcher_file}")
        
        # Copy to Desktop if accessible
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            try:
                dest = desktop / "Helper-AI.command"
                shutil.copy(launcher_file, dest)
                dest.chmod(0o755)
                print_success(f"Desktop launcher created: {dest}")
            except Exception:
                pass

    elif target_os == "linux":
        # Create user bin launcher
        user_bin = Path.home() / ".local" / "bin"
        user_bin.mkdir(parents=True, exist_ok=True)
        bin_script = user_bin / "helper-ai"
        with open(bin_script, "w") as f:
            f.write(f"#!/usr/bin/env bash\ncd '{root_dir}'\nexec python3 app.py \"$@\"\n")
        bin_script.chmod(0o755)
        print_success(f"Linux binary launcher installed at {bin_script}")

        # Desktop entry
        apps_dir = Path.home() / ".local" / "share" / "applications"
        apps_dir.mkdir(parents=True, exist_ok=True)
        desktop_file = apps_dir / "helper-ai.desktop"
        with open(desktop_file, "w") as f:
            f.write(f"""[Desktop Entry]
Name=Helper-AI
Comment=Autonomous PC Control & Internet Agent
Exec=bash -c "cd '{root_dir}' && python3 app.py"
Terminal=true
Type=Application
Categories=Utility;Development;
""")
        desktop_file.chmod(0o755)
        print_success(f"XDG Desktop application entry created: {desktop_file}")

    elif target_os == "android":
        termux_bin = Path(os.environ.get("PREFIX", "/data/data/com.termux/files/usr")) / "bin"
        if termux_bin.exists():
            t_script = termux_bin / "helper-ai"
            try:
                with open(t_script, "w") as f:
                    f.write(f"#!/data/data/com.termux/files/usr/bin/bash\ncd '{root_dir}'\npython3 app.py \"$@\"\n")
                t_script.chmod(0o755)
                print_success(f"Termux command 'helper-ai' registered in {t_script}")
            except Exception as e:
                print_step(f"Termux bin notice: {e}")

def main():
    root_dir = Path(__file__).resolve().parent
    target_os = detect_os()
    
    print_header(f"HELPER-AI: CROSS-PLATFORM SETUP ({target_os.upper()})")
    print_step(f"Installation directory: {root_dir}")
    
    check_python_version()
    setup_environment(root_dir)
    deps_ok = install_dependencies(root_dir)
    create_shortcuts(root_dir, target_os)
    
    print_header("INSTALLATION COMPLETE")
    print(f"To launch Helper-AI:")
    if target_os == "windows":
        print("  Run start.bat or double-click Helper-AI on your Desktop.")
    elif target_os == "macos":
        print("  Double-click Helper-AI.command on your Desktop or run: python3 app.py")
    elif target_os == "linux":
        print("  Launch 'helper-ai' in your terminal or search 'Helper-AI' in your app menu.")
    elif target_os == "android":
        print("  Type 'helper-ai' in Termux and open http://localhost:8000 in your browser.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
