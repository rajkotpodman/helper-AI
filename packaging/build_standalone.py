#!/usr/bin/env python3
"""
Helper-AI: Standalone Executable Packaging Script
Uses PyInstaller to generate native, standalone, portable binaries for Windows, Linux, and macOS.
"""
import os
import sys
import platform
import subprocess
import shutil
import tarfile
import zipfile
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def get_platform_info():
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system.startswith("win"):
        return "windows", "x64" if "64" in machine else "x86", "helper-ai.exe"
    elif system.startswith("darwin"):
        return "macos", "arm64" if "arm" in machine or "aarch" in machine else "x64", "helper-ai"
    elif system.startswith("linux"):
        return "linux", "x86_64" if "64" in machine else "x86", "helper-ai"
    return "unknown", machine, "helper-ai"

def build():
    root_dir = Path(__file__).resolve().parent.parent
    os_name, arch, bin_name = get_platform_info()
    sep = ";" if os_name == "windows" else ":"
    
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] Starting Standalone Build for {os_name.upper()} ({arch})...")
    print(f"[*] Workspace Root: {root_dir}")
    
    # Verify PyInstaller is installed
    try:
        import PyInstaller
        print(f"[OK] Found PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("[*] PyInstaller not found. Installing via pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # Collect data directories
    add_data_args = []
    for item in ["web/templates", "web/static", "static"]:
        p = root_dir / item
        if p.exists():
            add_data_args.extend(["--add-data", f"{p}{sep}{item}"])

    for single_file in [".env.example", "mcp_servers.json"]:
        p = root_dir / single_file
        if p.exists():
            add_data_args.extend(["--add-data", f"{p}{sep}."])

    # Hidden imports required by dynamic ASGI / FastAPI / automation tools
    hidden_imports = [
        "fastapi",
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "pydantic",
        "pydantic_core",
        "requests",
        "psutil",
        "rich",
        "selenium",
        "webdriver_manager",
        "pyautogui",
        "playwright",
        "edge_tts",
        "google_genai",
        "openai",
        "websockets",
        "aiohttp",
        "bs4",
        "duckduckgo_search",
        "ddgs"
    ]
    hidden_import_args = []
    for h in hidden_imports:
        hidden_import_args.extend(["--hidden-import", h])

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name", f"helper-ai-{os_name}-{arch}",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        *add_data_args,
        *hidden_import_args,
        str(root_dir / "app.py")
    ]

    print("[*] Running PyInstaller command:")
    print(" ".join(cmd))
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"[!] PyInstaller failed with exit code {res.returncode}")
        sys.exit(res.returncode)

    built_bin = dist_dir / f"helper-ai-{os_name}-{arch}"
    if os_name == "windows":
        built_bin = dist_dir / f"helper-ai-{os_name}-{arch}.exe"

    if built_bin.exists():
        print(f"[OK] Standalone binary compiled: {built_bin} ({built_bin.stat().st_size / (1024*1024):.2f} MB)")
        
        # Package into portable archive
        if os_name == "windows":
            zip_dest = dist_dir / f"Helper-AI-Windows-{arch}-Portable.zip"
            with zipfile.ZipFile(zip_dest, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(built_bin, arcname=f"helper-ai.exe")
                if (root_dir / "start.bat").exists():
                    zf.write(root_dir / "start.bat", arcname="start.bat")
                if (root_dir / "README.md").exists():
                    zf.write(root_dir / "README.md", arcname="README.md")
                if (root_dir / ".env.example").exists():
                    zf.write(root_dir / ".env.example", arcname=".env.example")
            print(f"[OK] Created Portable Windows Archive: {zip_dest}")
        else:
            tar_dest = dist_dir / f"Helper-AI-{os_name.capitalize()}-{arch}-Portable.tar.gz"
            with tarfile.open(tar_dest, "w:gz") as tf:
                tf.add(built_bin, arcname=f"helper-ai")
                if (root_dir / "README.md").exists():
                    tf.add(root_dir / "README.md", arcname="README.md")
                if (root_dir / ".env.example").exists():
                    tf.add(root_dir / ".env.example", arcname=".env.example")
            print(f"[OK] Created Portable Archive: {tar_dest}")

if __name__ == "__main__":
    build()
