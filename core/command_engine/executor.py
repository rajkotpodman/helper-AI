"""Universal Cross-Platform Terminal Command Execution Engine.

Executes terminal commands natively on Windows, Linux, and macOS, with
concurrency management, background daemon task tracking, auto-quoting,
and proactive self-healing error recovery.
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List

from core.command_engine.os_detector import OSDetector


class UniversalCommandExecutor:
    """Executes commands across any OS and shell with timeout and background support."""

    _background_tasks: Dict[str, Dict[str, Any]] = {}
    _lock = threading.Lock()

    @classmethod
    def execute_sync(
        cls,
        command: str,
        shell_type: Optional[str] = None,
        timeout_seconds: int = 120,
        cwd: Optional[str] = None,
        env_overrides: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executes a command synchronously on the host operating system.

        Args:
            command: Command string to execute.
            shell_type: 'powershell', 'cmd', 'posix' (bash/zsh), or None (auto-detect).
            timeout_seconds: Maximum time to wait before termination.
            cwd: Working directory.
            env_overrides: Custom environment variables.

        Returns:
            Dictionary containing exit code, stdout, stderr, execution time, and hints.
        """
        os_ctx = OSDetector.get_system_context()
        os_family = os_ctx["os"]["family"]
        pref_shell = os_ctx["preferred_shell"]

        # Determine binary and args
        target_shell = shell_type or pref_shell["type"]
        cmd_processed = cls._preprocess_command(command, os_family)

        exec_env = os.environ.copy()
        exec_env["CI"] = "true"
        exec_env["DEBIAN_FRONTEND"] = "noninteractive"
        if env_overrides:
            exec_env.update(env_overrides)

        if os_family == "windows":
            if target_shell in ["powershell", "pwsh"]:
                ps_bin = pref_shell["binary"] if "powershell" in pref_shell["binary"].lower() else "powershell.exe"
                cmd_args = [ps_bin, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd_processed]
            else:
                cmd_args = ["cmd.exe", "/c", cmd_processed]
        else:
            # POSIX (Linux / macOS / WSL)
            sh_bin = pref_shell["binary"] if os.path.exists(pref_shell.get("binary", "")) else "/bin/sh"
            cmd_args = [sh_bin, "-c", cmd_processed]

        start_time = time.perf_counter()
        try:
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=cwd,
                env=exec_env,
                encoding="utf-8",
                errors="replace"
            )
            elapsed = round(time.perf_counter() - start_time, 2)
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            output = stdout
            if stderr:
                output = f"{stdout}\n[STDERR]:\n{stderr}" if output else stderr

            success = (result.returncode == 0)
            hint = cls._generate_healing_hint(command, output, result.returncode, os_family)

            return {
                "success": success,
                "exit_code": result.returncode,
                "output": output,
                "stdout": stdout,
                "stderr": stderr,
                "elapsed_seconds": elapsed,
                "os_family": os_family,
                "shell_used": target_shell,
                "hint": hint
            }

        except subprocess.TimeoutExpired:
            elapsed = round(time.perf_counter() - start_time, 2)
            return {
                "success": False,
                "exit_code": -1,
                "output": f"Command timed out after {timeout_seconds} seconds.",
                "error": "TimeoutExpired",
                "elapsed_seconds": elapsed,
                "os_family": os_family,
                "hint": "Consider running this long task in the background using 'background: true' or increasing timeout."
            }
        except Exception as e:
            elapsed = round(time.perf_counter() - start_time, 2)
            return {
                "success": False,
                "exit_code": -1,
                "output": f"Failed to execute command: {str(e)}",
                "error": str(e),
                "elapsed_seconds": elapsed,
                "os_family": os_family,
                "hint": None
            }

    @classmethod
    def execute_background(
        cls,
        command: str,
        task_name: Optional[str] = None,
        cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Launches a heavy long-running process asynchronously in the background.

        Args:
            command: Command string to execute.
            task_name: Human-readable identifier.
            cwd: Working directory.

        Returns:
            Dictionary containing task_id and tracking status.
        """
        import uuid
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        os_ctx = OSDetector.get_system_context()
        os_family = os_ctx["os"]["family"]
        pref_shell = os_ctx["preferred_shell"]

        log_dir = Path.home() / ".helper_ai" / "task_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"{task_id}.log"

        cmd_processed = cls._preprocess_command(command, os_family)

        if os_family == "windows":
            ps_bin = pref_shell["binary"] if "powershell" in pref_shell["binary"].lower() else "powershell.exe"
            cmd_args = [ps_bin, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd_processed]
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        else:
            sh_bin = pref_shell["binary"] if os.path.exists(pref_shell.get("binary", "")) else "/bin/sh"
            cmd_args = [sh_bin, "-c", cmd_processed]
            creation_flags = 0

        log_file = open(log_path, "w", encoding="utf-8")
        proc = subprocess.Popen(
            cmd_args,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            creationflags=creation_flags
        )

        with cls._lock:
            cls._background_tasks[task_id] = {
                "task_id": task_id,
                "task_name": task_name or command[:40],
                "command": command,
                "process": proc,
                "start_time": time.time(),
                "log_path": str(log_path),
                "log_file": log_file
            }

        return {
            "success": True,
            "task_id": task_id,
            "status": "running",
            "log_file": str(log_path),
            "message": f"Heavy background task '{task_id}' started successfully."
        }

    @classmethod
    def get_task_status(cls, task_id: str) -> Dict[str, Any]:
        """Checks the execution status of a background task."""
        with cls._lock:
            task_info = cls._background_tasks.get(task_id)

        if not task_info:
            return {"success": False, "error": f"Task '{task_id}' not found."}

        proc = task_info["process"]
        poll = proc.poll()

        # Read last lines of log
        log_content = ""
        try:
            if os.path.exists(task_info["log_path"]):
                with open(task_info["log_path"], "r", encoding="utf-8", errors="replace") as f:
                    log_content = f.read()[-2000:]
        except Exception:
            pass

        if poll is None:
            return {
                "success": True,
                "task_id": task_id,
                "status": "running",
                "elapsed_seconds": round(time.time() - task_info["start_time"], 1),
                "recent_output": log_content
            }
        else:
            return {
                "success": True,
                "task_id": task_id,
                "status": "completed" if poll == 0 else "failed",
                "exit_code": poll,
                "elapsed_seconds": round(time.time() - task_info["start_time"], 1),
                "recent_output": log_content
            }

    @classmethod
    def kill_task(cls, task_id: str) -> Dict[str, Any]:
        """Terminates a running background task."""
        with cls._lock:
            task_info = cls._background_tasks.get(task_id)

        if not task_info:
            return {"success": False, "error": f"Task '{task_id}' not found."}

        proc = task_info["process"]
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

        return {"success": True, "task_id": task_id, "status": "terminated"}

    @staticmethod
    def _preprocess_command(command: str, os_family: str) -> str:
        """Auto-quotes unquoted Windows/POSIX drive paths containing spaces."""
        import re
        if os_family == "windows":
            path_match = re.search(r'([A-Za-z]:\\[^"\'\n\r;|]+)', command)
            if path_match:
                raw_path = path_match.group(1).strip()
                if " " in raw_path:
                    start_idx = path_match.start(1)
                    end_idx = path_match.end(1)
                    before = command[:start_idx]
                    after = command[end_idx:]
                    if not (before.endswith('"') or before.endswith("'")):
                        return f'{before}"{raw_path}"{after}'
        return command

    @staticmethod
    def _generate_healing_hint(command: str, output: str, exit_code: int, os_family: str) -> Optional[str]:
        """Provides dynamic self-healing advice if command failed."""
        if exit_code == 0:
            return None

        out_lower = output.lower()
        cmd_lower = command.lower()

        if "permission denied" in out_lower or "access is denied" in out_lower or "requires elevation" in out_lower:
            return (
                "Permission / Elevation Warning: This command requires elevated administrative privileges. "
                "On Windows, run the host terminal as Administrator. On Linux/macOS, use 'sudo'."
            )

        if "command not found" in out_lower or "not recognized as an internal or external command" in out_lower:
            cmd_first = command.strip().split()[0] if command.strip() else "tool"
            return (
                f"Binary '{cmd_first}' is not installed or not in PATH. "
                f"Use the host package manager or 'command_hub' tool to fetch installation instructions."
            )

        if "positional parameter cannot be found" in out_lower or "positionalparameternotfound" in out_lower:
            return "Path quoting error: A directory path containing spaces was not enclosed in quotes. Always wrap in double quotes: \"C:\\Path With Spaces\"."

        return None
