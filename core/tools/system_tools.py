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
        try:
            # We use powershell.exe on Windows or pwsh if available
            ps_binary = "powershell.exe" if platform.system() == "Windows" else "pwsh"
            result = subprocess.run(
                [ps_binary, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
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

            if not output:
                output = f"Command executed successfully with return code {result.returncode} (No output produced)."

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
        "Open any application, URL in the default browser, or open a file/folder "
        "in the Windows default program (e.g. notepad, calc, chrome, or explorer)."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Path to file/folder, URL (https://...), or application name (e.g. 'calc', 'notepad', 'explorer.exe')."
            }
        },
        "required": ["target"]
    }

    def execute(self, target: str) -> Dict[str, Any]:
        try:
            if platform.system() == "Windows":
                os.startfile(target)
            else:
                subprocess.Popen(["xdg-open", target])
            return {"success": True, "output": f"Launched '{target}' successfully."}
        except Exception as e:
            return {"success": False, "output": f"Failed to launch '{target}': {str(e)}", "error": str(e)}
