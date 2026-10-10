"""System and OS control tools for Helper-AI."""
import os
import platform
import subprocess
import psutil
from typing import Any, Dict
from core.tools.base import BaseTool

class ExecutePowerShellTool(BaseTool):
    name = "execute_powershell"
    description = (
        "Execute a PowerShell or Windows command directly on the host computer. "
        "Use this for installing packages, checking system settings, executing scripts, "
        "managing services, or any command-line task."
    )
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The exact PowerShell command line to execute."
            },
            "timeout_seconds": {
                "type": "integer",
                "description": "Maximum seconds to wait before terminating the command (default 90).",
                "default": 90
            }
        },
        "required": ["command"]
    }

    def execute(self, command: str, timeout_seconds: int = 90) -> Dict[str, Any]:
        cmd_lower = command.strip().lower()

        # Proactive interception: translate hallucinated PowerShell module commands for Ollama
        if "get-installedmodule" in cmd_lower and ("ollama" in cmd_lower or "model" in cmd_lower):
            try:
                res = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=8)
                if res.returncode == 0 and res.stdout.strip():
                    return {
                        "success": True,
                        "exit_code": 0,
                        "output": f"Successfully retrieved installed Ollama models:\n{res.stdout.strip()}",
                        "error": None
                    }
            except Exception:
                pass

        if "install-module" in cmd_lower and ("powershellget" in cmd_lower or "ollama" in cmd_lower):
            return {
                "success": False,
                "exit_code": 1,
                "output": "Action halted: 'Install-Module' is not appropriate here. Ollama is a standalone CLI program. Use 'manage_ollama' tool or run 'ollama list' directly.",
                "error": "InvalidApproach"
            }

        # Proactive auto-quoting for unquoted drive paths with spaces
        import re
        cmd_processed = command
        path_match = re.search(r'([A-Za-z]:\\[^"\'\n\r;|]+)', command)
        if path_match:
            raw_path = path_match.group(1).strip()
            # If path has spaces and is not already wrapped in quotes
            if " " in raw_path:
                start_idx = path_match.start(1)
                end_idx = path_match.end(1)
                before = command[:start_idx]
                after = command[end_idx:]
                if not (before.endswith('"') or before.endswith("'")):
                    cmd_processed = f'{before}"{raw_path}"{after}'

        try:
            # We use powershell.exe on Windows or pwsh if available
            ps_binary = "powershell.exe" if platform.system() == "Windows" else "pwsh"
            result = subprocess.run(
                [ps_binary, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd_processed],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                encoding="utf-8",
                errors="replace"
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            output = ""
            if stdout:
                output += stdout
            if stderr:
                if output:
                    output += "\n[STDERR]:\n"
                output += stderr

            if result.returncode != 0:
                # If command failed and was looking for Ollama, perform immediate self-healing recovery
                if ("ollama" in cmd_lower or "model" in cmd_lower) and "powershellget" in output.lower():
                    try:
                        res = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=8)
                        if res.returncode == 0 and res.stdout.strip():
                            return {
                                "success": True,
                                "exit_code": 0,
                                "output": f"Self-healing recovery executed: Retrieved installed Ollama models directly:\n{res.stdout.strip()}",
                                "error": None
                            }
                    except Exception:
                        pass

                # If failed due to PositionalParameterNotFound (unquoted path with spaces)
                if "positional parameter cannot be found" in output.lower() or "positionalparameternotfound" in output.lower():
                    p_match = re.search(r'([A-Za-z]:\\[^\n\r]+)', command)
                    if p_match:
                        raw_cand = p_match.group(1).strip()
                        if os.path.exists(raw_cand):
                            # Self-heal by executing Get-ChildItem with quotes or running list_directory
                            heal_cmd = f'Get-ChildItem "{raw_cand}"'
                            h_res = subprocess.run(
                                [ps_binary, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", heal_cmd],
                                capture_output=True, text=True, timeout=timeout_seconds, encoding="utf-8", errors="replace"
                            )
                            if h_res.returncode == 0 and h_res.stdout.strip():
                                return {
                                    "success": True,
                                    "exit_code": 0,
                                    "output": f"Self-healing recovery: Automatically quoted folder path with spaces:\n{h_res.stdout.strip()}",
                                    "error": None
                                }

            if result.returncode != 0:
                hint = ""
                cmd_lower = command.lower()
                if "positional parameter cannot be found" in output.lower() or "positionalparameternotfound" in output.lower():
                    hint = "\n[SELF-HEALING HINT]: You forgot to enclose a path with spaces in quotes! In PowerShell, always use quotes: Get-ChildItem \"E:\\Path With Spaces\". Better yet, use the 'list_directory' tool!"
                elif "get-installedmodule" in cmd_lower or "install-module" in cmd_lower:
                    hint = "\n[SELF-HEALING HINT]: 'Get-InstalledModule' only checks PowerShell Gallery modules and is not available on this system. If you want to check Ollama models, run 'ollama list' or use the 'manage_ollama' tool. For installed Windows applications, run 'winget list' or 'Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*'."
                elif "ollama" in cmd_lower and ("not recognized" in output.lower() or "not found" in output.lower()):
                    hint = "\n[SELF-HEALING HINT]: 'ollama' is at 'C:\\Users\\DELL\\AppData\\Local\\Programs\\Ollama\\ollama.exe', or check 'http://localhost:11434/api/tags' via curl/Invoke-RestMethod."
                elif "sendkeys" in cmd_lower or "sendwait" in cmd_lower or "uiautomation" in cmd_lower:
                    hint = "\n[SELF-HEALING HINT]: PowerShell SendKeys/UIAutomation is blocked by Windows UI security or process isolation. Use the 'browser_automation' tool directly (with action 'type', 'click', or 'publish_facebook_post') to interact with browser web pages!"
                if hint:
                    output += hint

            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "output": output,
                "error": stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "exit_code": -1,
                "output": f"Command timed out after {timeout_seconds} seconds.",
                "error": "TimeoutExpired"
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "output": f"Execution error: {str(e)}",
                "error": str(e)
            }


class GetSystemHealthTool(BaseTool):
    name = "get_system_health"
    description = (
        "Check system health, hardware status, OS details, CPU usage, RAM consumption, "
        "disk space availability, and battery status."
    )
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            cpu_pct = psutil.cpu_percent(interval=0.5)
            cpu_count = psutil.cpu_count(logical=True)
            mem = psutil.virtual_memory()
            disks = []
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disks.append({
                        "mountpoint": part.mountpoint,
                        "device": part.device,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "percent": usage.percent
                    })
                except (PermissionError, OSError):
                    continue

            battery_info = None
            if hasattr(psutil, "sensors_battery"):
                b = psutil.sensors_battery()
                if b:
                    battery_info = {
                        "percent": b.percent,
                        "power_plugged": b.power_plugged,
                        "secsleft": b.secsleft
                    }

            summary = {
                "os": f"{platform.system()} {platform.release()} ({platform.version()})",
                "machine": platform.machine(),
                "node_name": platform.node(),
                "cpu_percent": cpu_pct,
                "cpu_cores": cpu_count,
                "ram_total_gb": round(mem.total / (1024**3), 2),
                "ram_used_gb": round(mem.used / (1024**3), 2),
                "ram_available_gb": round(mem.available / (1024**3), 2),
                "ram_percent": mem.percent,
                "disks": disks,
                "battery": battery_info
            }

            output = (
                f"OS: {summary['os']}\n"
                f"CPU: {summary['cpu_percent']}% across {summary['cpu_cores']} cores\n"
                f"RAM: {summary['ram_used_gb']}GB / {summary['ram_total_gb']}GB used ({summary['ram_percent']}%)\n"
                f"Disks:\n" + "\n".join([f"  - {d['mountpoint']} {d['free_gb']}GB free / {d['total_gb']}GB ({d['percent']}% used)" for d in disks])
            )
            if battery_info:
                plugged = "Plugged In" if battery_info["power_plugged"] else "On Battery"
                output += f"\nBattery: {battery_info['percent']}% ({plugged})"

            return {
                "success": True,
                "output": output,
                "raw_data": summary
            }
        except Exception as e:
            return {"success": False, "output": f"Failed to retrieve system health: {str(e)}", "error": str(e)}


class ProcessManagerTool(BaseTool):
    name = "manage_processes"
    description = "List running processes (sorted by memory or CPU) or terminate an unresponsive process by PID or Name."
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "kill"],
                "description": "'list' to view top processes, 'kill' to terminate a process."
            },
            "pid": {
                "type": "integer",
                "description": "Process ID (required when action is 'kill' unless process_name is provided)."
            },
            "process_name": {
                "type": "string",
                "description": "Process name e.g. 'notepad.exe' (optional)."
            },
            "sort_by": {
                "type": "string",
                "enum": ["memory", "cpu"],
                "description": "How to sort listed processes (default 'memory').",
                "default": "memory"
            },
            "limit": {
                "type": "integer",
                "description": "Number of processes to list (default 15).",
                "default": 15
            }
        },
        "required": ["action"]
    }

    def execute(self, action: str, pid: int = None, process_name: str = None, sort_by: str = "memory", limit: int = 15) -> Dict[str, Any]:
        try:
            if action == "list":
                procs = []
                for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        procs.append(p.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                key = 'memory_percent' if sort_by == 'memory' else 'cpu_percent'
                procs.sort(key=lambda x: x.get(key) or 0, reverse=True)
                top = procs[:limit]

                lines = [f"{'PID':<8} {'Name':<28} {'CPU %':<8} {'Memory %':<8}"]
                lines.append("-" * 56)
                for p in top:
                    name = (p.get('name') or "Unknown")[:26]
                    cpu = round(p.get('cpu_percent') or 0, 1)
                    mem = round(p.get('memory_percent') or 0, 1)
                    lines.append(f"{p['pid']:<8} {name:<28} {cpu:<8} {mem:<8}")

                return {"success": True, "output": "\n".join(lines)}

            elif action == "kill":
                killed = []
                if pid:
                    p = psutil.Process(pid)
                    p_name = p.name()
                    p.terminate()
                    killed.append(f"PID {pid} ({p_name})")
                elif process_name:
                    for p in psutil.process_iter(['pid', 'name']):
                        try:
                            if p.info['name'] and p.info['name'].lower() == process_name.lower():
                                p.terminate()
                                killed.append(f"PID {p.info['pid']} ({p.info['name']})")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                else:
                    return {"success": False, "output": "Provide either 'pid' or 'process_name' to kill a process."}

                if killed:
                    return {"success": True, "output": f"Successfully terminated: {', '.join(killed)}"}
                else:
                    return {"success": False, "output": f"No running process matched the given criteria."}
            else:
                return {"success": False, "output": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "output": f"Process manager error: {str(e)}", "error": str(e)}


class OpenAppOrFileTool(BaseTool):
    name = "open_app_or_file"
    description = (
        "Open any application (Edge, Chrome, Notepad, Calc, Explorer, etc.), "
        "URL in default browser (https://...), or open a file/folder in its default program."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Application name (e.g. 'edge', 'chrome', 'notepad', 'calc'), URL, or file/folder path."
            }
        },
        "required": ["target"]
    }

    APP_MAP = {
        "edge": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            "msedge.exe"
        ],
        "microsoft edge": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            "msedge.exe"
        ],
        "edge browser": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            "msedge.exe"
        ],
        "edge borwser": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            "msedge.exe"
        ],
        "msedge": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            "msedge.exe"
        ],
        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "chrome.exe"
        ],
        "chrome browser": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "chrome.exe"
        ],
        "google chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "chrome.exe"
        ],
        "notepad": ["notepad.exe"],
        "calc": ["calc.exe"],
        "calculator": ["calc.exe"],
        "explorer": ["explorer.exe"],
        "file explorer": ["explorer.exe"]
    }

    def execute(self, target: str = None, app_name: str = None, name: str = None, path: str = None, **kwargs) -> Dict[str, Any]:
        import shutil
        raw = (target or app_name or name or path or "").strip()
        if not raw:
            return {"success": False, "output": "Please provide a valid application name, URL, or file path."}

        # Handle web URLs
        if raw.startswith("http://") or raw.startswith("https://") or raw.startswith("microsoft-edge:"):
            try:
                if platform.system() == "Windows":
                    os.startfile(raw)
                else:
                    import webbrowser
                    webbrowser.open(raw)
                return {"success": True, "output": f"Opened URL '{raw}' in browser successfully."}
            except Exception:
                import webbrowser
                webbrowser.open(raw)
                return {"success": True, "output": f"Opened URL '{raw}' via system browser."}

        # Check if command has arguments (e.g. 'msedge https://bing.com')
        parts = raw.split(" ", 1)
        app_key = parts[0].lower().strip().replace('"', '').replace("'", "")
        args_part = parts[1].strip() if len(parts) > 1 else ""

        # Filter out noise words from args_part
        if args_part:
            clean_arg = args_part.lower().strip().replace('"', '').replace("'", "")
            if clean_arg in ["browser", "borwser", "app", "application", "window", "pls", "please"]:
                args_part = ""

        # Check known apps
        resolved_exe = None
        for key_cand, exes in self.APP_MAP.items():
            if raw.lower() == key_cand or app_key == key_cand:
                for cand in exes:
                    if os.path.exists(cand) or shutil.which(cand):
                        resolved_exe = cand
                        break
                if resolved_exe:
                    break

        if resolved_exe:
            try:
                cmd_list = [resolved_exe]
                if args_part:
                    cmd_list.append(args_part)
                subprocess.Popen(cmd_list)
                return {"success": True, "output": f"Launched '{raw}' successfully using '{resolved_exe}'."}
            except Exception as e:
                pass

        # Try os.startfile directly for files/registered apps
        try:
            if platform.system() == "Windows":
                os.startfile(raw)
            else:
                subprocess.Popen(["xdg-open", raw])
            return {"success": True, "output": f"Launched '{raw}' successfully."}
        except Exception:
            # Fallback to PowerShell Start-Process
            try:
                cmd = f'Start-Process "{raw}"'
                subprocess.Popen(["powershell.exe", "-NoProfile", "-Command", cmd])
                return {"success": True, "output": f"Launched '{raw}' via PowerShell Start-Process."}
            except Exception as e:
                return {"success": False, "output": f"Failed to launch '{raw}': {str(e)}", "error": str(e)}


class ManageOllamaTool(BaseTool):
    name = "manage_ollama"
    description = (
        "Inspect, list, query, or check status of local Ollama AI models. "
        "Use this tool whenever the user asks about Ollama, checking installed Ollama models, "
        "running models, or local AI model details."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list_models", "status", "running_models"],
                "description": "Action to perform: 'list_models' to view installed models, 'status' to check service health, 'running_models' to check currently loaded models in RAM.",
                "default": "list_models"
            }
        },
        "required": ["action"]
    }

    def execute(self, action: str = "list_models") -> Dict[str, Any]:
        import json
        import requests
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip('/')

        # Ensure daemon is running
        try:
            requests.get(f"{base_url}/api/version", timeout=2)
        except Exception:
            try:
                creation_flags = 0
                if os.name == "nt":
                    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
                subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creation_flags)
                import time
                time.sleep(1.2)
            except Exception:
                pass

        if action == "list_models":
            try:
                r = requests.get(f"{base_url}/api/tags", timeout=5)
                if r.status_code == 200:
                    models = r.json().get("models", [])
                    if models:
                        lines = [f"Found {len(models)} installed Ollama model(s):"]
                        for m in models:
                            size_mb = round(m.get("size", 0) / (1024 * 1024), 1)
                            size_str = f"{round(size_mb / 1024, 2)} GB" if size_mb >= 1024 else f"{size_mb} MB"
                            lines.append(f"- Model: {m.get('name')} (Size: {size_str}, ID: {m.get('digest', '')[:12]})")
                        return {"success": True, "output": "\n".join(lines)}
                    else:
                        return {"success": True, "output": "No Ollama models currently downloaded. Run 'ollama pull <model>' to download one."}
            except Exception:
                pass

            # Fallback to CLI
            try:
                res = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=8)
                if res.returncode == 0 and res.stdout.strip():
                    return {"success": True, "output": res.stdout.strip()}
            except Exception as e:
                return {"success": False, "output": f"Could not list Ollama models: {str(e)}", "error": str(e)}

            return {"success": False, "output": f"Ollama service is not reachable at {base_url}."}

        elif action == "running_models":
            try:
                r = requests.get(f"{base_url}/api/ps", timeout=5)
                if r.status_code == 200:
                    models = r.json().get("models", [])
                    if models:
                        return {"success": True, "output": f"Currently loaded models in memory: {json.dumps(models, indent=2)}"}
                    return {"success": True, "output": "No models are currently loaded in RAM."}
            except Exception as e:
                return {"success": False, "output": f"Failed to check running models: {str(e)}"}

        elif action == "status":
            try:
                r = requests.get(f"{base_url}/api/version", timeout=3)
                if r.status_code == 200:
                    return {"success": True, "output": f"Ollama service is active and healthy (version {r.json().get('version')}) at {base_url}."}
            except Exception:
                return {"success": False, "output": f"Ollama service is currently not responding at {base_url}."}

        return {"success": False, "output": f"Unknown action: {action}"}
