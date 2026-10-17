"""Persistent Stateful Shell Session Engine (Open Interpreter Pattern).

Maintains a live, interactive PowerShell (Windows) or Bash/sh (POSIX) process
across multiple tool steps. Preserves working directory (`cd`), environment variables,
virtual environments, and shell functions.
"""

import os
import sys
import time
import uuid
import queue
import logging
import threading
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from core.command_engine.os_detector import OSDetector

logger = logging.getLogger("PersistentShell")


class PersistentShellSession:
    """Manages a single continuous, stateful interactive shell subprocess."""

    def __init__(self, session_id: str = "default", shell_type: Optional[str] = None):
        self.session_id = session_id
        self.shell_type = shell_type
        self.process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._output_queue: queue.Queue = queue.Queue()
        self._reader_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._current_cwd: str = os.getcwd()
        self._command_count: int = 0
        self._created_at: float = time.time()
        self._os_family: str = OSDetector.get_system_context()["os"]["family"]

        self._start_process()

    def _get_shell_command(self) -> List[str]:
        if self._os_family == "windows":
            # Use PowerShell with NoProfile, NoLogo, Bypass execution policy
            return [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass"
            ]
        else:
            # POSIX: bash or sh
            for sh in ["/bin/bash", "/usr/bin/bash", "/bin/sh"]:
                if os.path.exists(sh):
                    return [sh]
            return ["sh"]

    def _start_process(self) -> None:
        """Starts or restarts the background shell subprocess."""
        self._stop_event.set()
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass

        self._stop_event.clear()
        self._output_queue = queue.Queue()

        cmd = self._get_shell_command()
        env = os.environ.copy()
        env["CI"] = "true"
        env["TERM"] = "dumb"

        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace",
                env=env,
                cwd=self._current_cwd
            )

            # Spawn reader thread to continuously read stdout into queue
            self._reader_thread = threading.Thread(
                target=self._read_stdout,
                args=(self.process, self._output_queue, self._stop_event),
                daemon=True,
                name=f"ShellReader-{self.session_id}"
            )
            self._reader_thread.start()
            logger.info(f"Started persistent shell session '{self.session_id}' ({cmd[0]}) in {self._current_cwd}")

        except Exception as e:
            logger.error(f"Failed to start persistent shell process: {e}")
            self.process = None

    @staticmethod
    def _read_stdout(proc: subprocess.Popen, q: queue.Queue, stop_ev: threading.Event):
        """Worker thread that drains stdout line by line into the thread-safe queue."""
        try:
            for line in iter(proc.stdout.readline, ""):
                if stop_ev.is_set():
                    break
                q.put(line)
        except Exception:
            pass
        finally:
            proc.stdout.close()

    def is_alive(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def execute(self, command: str, timeout_seconds: int = 120) -> Dict[str, Any]:
        """
        Executes a command within the persistent shell session.

        State (variables, directory changes, active envs) is preserved for subsequent calls.
        """
        with self._lock:
            if not self.is_alive():
                logger.warning(f"Shell session '{self.session_id}' not alive. Restarting...")
                self._start_process()
                if not self.is_alive():
                    return {
                        "success": False,
                        "exit_code": -1,
                        "output": "Failed to initialize persistent shell subprocess.",
                        "error": "ProcessSpawnError",
                        "session_id": self.session_id,
                        "cwd": self._current_cwd
                    }

            # Drain any stale leftover output from previous commands
            while not self._output_queue.empty():
                try:
                    self._output_queue.get_nowait()
                except queue.Empty:
                    break

            # Generate unique token to identify end of output
            token_id = uuid.uuid4().hex[:12]
            sentinel = f"__HELPER_AI_SENTINEL_{token_id}__"

            # Construct command with metadata capture
            if self._os_family == "windows":
                # PowerShell: capture exit code and current working directory
                # Use $($var) subexpression to prevent ':' being parsed as a drive scope
                wrapped_cmd = (
                    f"{command}\n"
                    f"$__ha_pwd = (Get-Location).Path\n"
                    f"$__ha_ec = $LASTEXITCODE; if ($null -eq $__ha_ec) {{ $__ha_ec = 0 }}\n"
                    f"Write-Output \"{sentinel}::$($__ha_pwd)::$($__ha_ec)\"\n"
                )
            else:
                # POSIX (Bash/sh)
                wrapped_cmd = (
                    f"{command}\n"
                    f"__ha_ec=$?\n"
                    f"__ha_pwd=$(pwd)\n"
                    f"echo \"{sentinel}::$__ha_pwd::$__ha_ec\"\n"
                )

            start_time = time.perf_counter()

            try:
                self.process.stdin.write(wrapped_cmd)
                self.process.stdin.flush()
            except Exception as e:
                # Process stdin write failed (process may have died)
                logger.error(f"Error writing to shell stdin: {e}")
                self._start_process()
                return {
                    "success": False,
                    "exit_code": -1,
                    "output": f"Shell pipe error: {e}. Session restarted.",
                    "error": str(e),
                    "session_id": self.session_id,
                    "cwd": self._current_cwd
                }

            # Read from queue until sentinel is encountered or timeout expired
            collected_lines: List[str] = []
            meta_cwd: Optional[str] = None
            meta_exit_code: int = 0
            found_sentinel = False
            deadline = time.time() + timeout_seconds

            while time.time() < deadline:
                try:
                    line = self._output_queue.get(timeout=0.2)
                except queue.Empty:
                    if not self.is_alive():
                        collected_lines.append("\n[Process exited prematurely]")
                        break
                    continue

                # Ignore prompt echoes and command input echo lines
                sline = line.strip()
                if (sline.startswith("PS ") and ">" in sline) or ("Write-Output" in sline and sentinel in sline) or ("echo " in sline and sentinel in sline):
                    continue

                if sentinel in line:
                    found_sentinel = True
                    # Parse evaluated sentinel line: SENTINEL::CWD::EXIT_CODE
                    try:
                        meta_part = line.strip().split(sentinel + "::")
                        if len(meta_part) > 1:
                            parts = meta_part[1].split("::")
                            if len(parts) >= 2:
                                meta_cwd = parts[0].strip()
                                meta_exit_code = int(parts[1].strip())
                            elif len(parts) == 1:
                                meta_cwd = parts[0].strip()
                    except Exception:
                        pass
                    break
                else:
                    collected_lines.append(line)

            elapsed = round(time.perf_counter() - start_time, 2)
            self._command_count += 1

            if not found_sentinel:
                # Timeout occurred
                return {
                    "success": False,
                    "exit_code": -1,
                    "output": "".join(collected_lines).strip() + f"\n[Command timed out after {timeout_seconds}s]",
                    "error": "TimeoutExpired",
                    "elapsed_seconds": elapsed,
                    "session_id": self.session_id,
                    "cwd": self._current_cwd,
                    "hint": "The command may be waiting for user input. Use non-interactive flags or background execution."
                }

            # Update working directory if changed
            if meta_cwd and os.path.isdir(meta_cwd):
                self._current_cwd = meta_cwd

            raw_output = "".join(collected_lines)
            cleaned_output = self._clean_shell_output(raw_output, command)

            success = (meta_exit_code == 0)

            return {
                "success": success,
                "exit_code": meta_exit_code,
                "output": cleaned_output,
                "elapsed_seconds": elapsed,
                "session_id": self.session_id,
                "cwd": self._current_cwd,
                "command_count": self._command_count,
                "persistent": True
            }

    def _clean_shell_output(self, raw: str, orig_cmd: str) -> str:
        """Cleans prompt echoes and noise from shell output."""
        lines = raw.splitlines()
        filtered = []
        for line in lines:
            sline = line.strip()
            if not sline:
                continue
            if sline.startswith("$__ha_") or "__ha_pwd=" in sline or "__ha_ec=" in sline:
                continue
            if "__HELPER_AI_SENTINEL" in sline or ("Write-Output" in sline and "SENTINEL" in sline):
                continue
            if sline == orig_cmd.strip():
                continue
            if sline.startswith("PS ") and (">" in sline):
                # Filter prompt echo
                if any(x in sline for x in [orig_cmd.strip(), "$__ha_", "Write-Output", "echo"]):
                    continue
            filtered.append(line)
        return "\n".join(filtered).strip()

    def reset(self) -> Dict[str, Any]:
        """Resets the persistent shell session to a fresh state."""
        with self._lock:
            self._start_process()
            self._command_count = 0
            return {
                "success": True,
                "message": f"Persistent shell session '{self.session_id}' has been reset.",
                "session_id": self.session_id,
                "cwd": self._current_cwd
            }

    def get_info(self) -> Dict[str, Any]:
        """Returns metadata about the active shell session."""
        return {
            "session_id": self.session_id,
            "is_alive": self.is_alive(),
            "cwd": self._current_cwd,
            "command_count": self._command_count,
            "os_family": self._os_family,
            "uptime_seconds": round(time.time() - self._created_at, 1)
        }

    def close(self) -> None:
        """Terminates the shell process."""
        self._stop_event.set()
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None


class PersistentShellManager:
    """Singleton registry for persistent shell sessions."""

    _sessions: Dict[str, PersistentShellSession] = {}
    _lock = threading.Lock()

    @classmethod
    def get_session(cls, session_id: str = "default") -> PersistentShellSession:
        """Gets or creates a persistent shell session by ID."""
        with cls._lock:
            if session_id not in cls._sessions or not cls._sessions[session_id].is_alive():
                cls._sessions[session_id] = PersistentShellSession(session_id=session_id)
            return cls._sessions[session_id]

    @classmethod
    def reset_session(cls, session_id: str = "default") -> Dict[str, Any]:
        """Resets the specified session."""
        with cls._lock:
            if session_id in cls._sessions:
                return cls._sessions[session_id].reset()
            sess = PersistentShellSession(session_id=session_id)
            cls._sessions[session_id] = sess
            return sess.get_info()

    @classmethod
    def list_sessions(cls) -> Dict[str, Any]:
        """Lists all active shell sessions."""
        with cls._lock:
            return {
                "active_sessions": {
                    s_id: sess.get_info()
                    for s_id, sess in cls._sessions.items()
                }
            }

    @classmethod
    def close_all(cls) -> None:
        """Closes all active sessions."""
        with cls._lock:
            for sess in cls._sessions.values():
                sess.close()
            cls._sessions.clear()
