"""Microsoft Playwright Integration & CRM Workflow Manager for Helper-AI.

Provides:
1. Playwright Codegen Launcher (Live interactive recording in Chrome with Inspector).
2. Workflow Storage State management (saved cookies & sessions for zero-re-login).
3. Heavy / Long-running CRM Batch Execution (looping over Excel/CSV lead datasets).
4. Automated Script Parameterization and Robust Error Recovery.
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger("PlaywrightManager")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = PROJECT_ROOT / "workflows" / "playwright"
STORAGE_DIR = PROJECT_ROOT / "workflows" / "storage"

WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


class PlaywrightManager:
    """Manages Playwright Codegen recording, session persistence, and CRM batch replay."""

    _instance: Optional["PlaywrightManager"] = None

    @classmethod
    def get_instance(cls) -> "PlaywrightManager":
        if cls._instance is None:
            cls._instance = PlaywrightManager()
        return cls._instance

    def __init__(self):
        self._active_codegen_process: Optional[subprocess.Popen] = None
        self._active_run_process: Optional[subprocess.Popen] = None
        self._is_running_workflow = False
        self._last_run_logs: List[str] = []

    def get_status(self) -> Dict[str, Any]:
        """Inspects Playwright availability and local browser readiness."""
        installed = False
        version_str = "not_installed"
        try:
            import playwright
            from importlib.metadata import version
            version_str = version("playwright")
            installed = True
        except Exception:
            pass

        workflows = self.list_workflows()
        sessions = [f.stem for f in STORAGE_DIR.glob("*.json")]

        return {
            "installed": installed,
            "playwright_installed": installed,
            "version": version_str,
            "codegen_active": self.is_codegen_running(),
            "active_codegen": self.is_codegen_running(),
            "workflow_running": self._is_running_workflow,
            "workflows_count": len(workflows),
            "workflows": workflows,
            "saved_sessions": sessions,
            "workflows_directory": str(WORKFLOWS_DIR),
            "storage_directory": str(STORAGE_DIR)
        }

    def is_codegen_running(self) -> bool:
        if self._active_codegen_process is not None:
            if self._active_codegen_process.poll() is None:
                return True
            self._active_codegen_process = None
        return False

    def launch_codegen(
        self,
        url: Optional[str] = None,
        workflow_name: Optional[str] = None,
        target_lang: str = "python",
        use_chrome: bool = True,
        save_session: bool = True,
        session_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Launches real Chrome with Playwright Inspector side-by-side to record user actions.
        
        Args:
            url: Starting URL (e.g. Tata CRM login or form page).
            workflow_name: Name for the output file (e.g. 'tata_crm_lead_entry').
            target_lang: Language to generate ('python', 'javascript', etc.).
            use_chrome: Whether to launch installed Google Chrome instead of Chromium.
            save_session: Whether to save authentication cookies & localStorage to session_name.
            session_name: Key name for session persistence (e.g. 'tata_crm_session').
        """
        if self.is_codegen_running():
            return {
                "success": False,
                "error": "A Playwright Codegen recording session is already active.",
                "pid": self._active_codegen_process.pid if self._active_codegen_process else None
            }

        name_slug = (workflow_name or f"crm_workflow_{int(time.time())}").strip().replace(" ", "_")
        if not name_slug.endswith(".py"):
            name_slug += ".py"

        out_path = WORKFLOWS_DIR / name_slug
        session_slug = (session_name or "default_session").strip().replace(" ", "_")
        storage_file = STORAGE_DIR / f"{session_slug}.json"

        cmd = [sys.executable, "-m", "playwright", "codegen"]
        
        # Output script target
        cmd.extend(["-o", str(out_path)])
        cmd.extend(["--target", target_lang])

        # Prefer system Google Chrome if available
        if use_chrome:
            cmd.extend(["--channel", "chrome"])

        # Load existing storage state if available
        if storage_file.exists():
            cmd.extend(["--load-storage", str(storage_file)])

        # Save storage state on exit
        if save_session:
            cmd.extend(["--save-storage", str(storage_file)])

        # Target starting URL
        if url and url.strip():
            cmd.append(url.strip())

        logger.info(f"Launching Playwright Codegen: {' '.join(cmd)}")
        try:
            # Launch detached window so user can interact with Chrome & Inspector
            proc = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
            )
            self._active_codegen_process = proc
            return {
                "success": True,
                "message": f"Playwright Codegen launched. Interacting in Chrome will generate code in {out_path.name}",
                "workflow_file": str(out_path),
                "workflow_name": out_path.name,
                "pid": proc.pid
            }
        except Exception as e:
            logger.error(f"Failed to launch Playwright Codegen: {e}")
            return {"success": False, "error": str(e)}

    def stop_codegen(self) -> Dict[str, Any]:
        """Terminates active Codegen recording session."""
        if self._active_codegen_process is not None:
            try:
                self._active_codegen_process.terminate()
                self._active_codegen_process = None
                return {"success": True, "message": "Playwright Codegen session stopped."}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": True, "message": "No active Codegen session."}

    def list_workflows(self) -> List[Dict[str, Any]]:
        """Lists all recorded Playwright automation workflows."""
        results = []
        for p in WORKFLOWS_DIR.glob("*.py"):
            try:
                stat = p.stat()
                mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
                code_text = p.read_text(encoding="utf-8", errors="ignore")
                results.append({
                    "name": p.name,
                    "filename": p.name,
                    "stem": p.stem,
                    "path": str(p),
                    "size_bytes": stat.st_size,
                    "modified": mtime,
                    "lines_count": len(code_text.splitlines()),
                    "has_parameters": ("{{" in code_text and "}}" in code_text)
                })
            except Exception:
                continue
        return sorted(results, key=lambda x: x["name"])

    def get_workflow(self, name: str) -> Dict[str, Any]:
        """Fetches workflow code and metadata."""
        clean_name = name if name.endswith(".py") else f"{name}.py"
        path = WORKFLOWS_DIR / clean_name
        if not path.exists():
            return {"success": False, "error": f"Workflow {clean_name} not found."}

        code = path.read_text(encoding="utf-8", errors="ignore")
        return {
            "success": True,
            "found": True,
            "name": path.name,
            "filename": path.name,
            "path": str(path),
            "code": code,
            "lines_count": len(code.splitlines())
        }

    def save_workflow(self, name: str, code: str) -> Dict[str, Any]:
        """Saves or edits a workflow Python script."""
        clean_name = name if name.endswith(".py") else f"{name}.py"
        path = WORKFLOWS_DIR / clean_name
        path.write_text(code, encoding="utf-8")
        return {
            "success": True,
            "status": "saved",
            "message": f"Workflow {clean_name} saved successfully.",
            "path": str(path)
        }

    def run_workflow_standalone(
        self,
        name: str,
        timeout_seconds: int = 180
    ) -> Dict[str, Any]:
        """Runs a recorded Playwright script standalone directly."""
        clean_name = name if name.endswith(".py") else f"{name}.py"
        path = WORKFLOWS_DIR / clean_name
        if not path.exists():
            return {"success": False, "error": f"Workflow {clean_name} not found."}

        self._is_running_workflow = True
        self._last_run_logs = []

        try:
            cmd = [sys.executable, str(path)]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=str(PROJECT_ROOT)
            )
            out = proc.stdout or ""
            err = proc.stderr or ""
            self._last_run_logs.append(out)
            if err:
                self._last_run_logs.append(err)

            success = (proc.returncode == 0)
            return {
                "success": success,
                "workflow": clean_name,
                "returncode": proc.returncode,
                "output": out,
                "error": err if not success else None
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Workflow execution timed out after {timeout_seconds}s."}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            self._is_running_workflow = False

    def run_workflow_batch(
        self,
        name: str,
        data_records: List[Dict[str, Any]],
        delay_between_records_s: float = 1.0,
        stop_on_error: bool = False
    ) -> Dict[str, Any]:
        """Executes a recorded workflow parameterized across a list of data rows (e.g. from Excel/CSV).
        
        Args:
            name: Workflow script filename.
            data_records: List of key-value dictionaries (e.g. [{"name": "Rahul", "mobile": "9898012345"}]).
            delay_between_records_s: Wait time between successive form submissions.
            stop_on_error: If True, halts immediately on first failure.
        """
        clean_name = name if name.endswith(".py") else f"{name}.py"
        path = WORKFLOWS_DIR / clean_name
        if not path.exists():
            return {"success": False, "error": f"Workflow {clean_name} not found."}

        template_code = path.read_text(encoding="utf-8", errors="ignore")
        total_rows = len(data_records)
        completed_rows = 0
        failed_rows = 0
        record_logs: List[Dict[str, Any]] = []

        self._is_running_workflow = True

        try:
            for idx, row in enumerate(data_records):
                row_num = idx + 1
                row_code = template_code
                
                # Replace placeholders like {{name}} or case-insensitive matching
                for key, val in row.items():
                    val_str = str(val) if val is not None else ""
                    # Direct template placeholder {{key}}
                    row_code = row_code.replace(f"{{{{{key}}}}}", val_str)
                    row_code = row_code.replace(f"{{{{{key.lower()}}}}}", val_str)

                # Execute row script in isolated temporary execution
                temp_run_path = WORKFLOWS_DIR / f"_temp_run_row_{row_num}.py"
                temp_run_path.write_text(row_code, encoding="utf-8")

                try:
                    proc = subprocess.run(
                        [sys.executable, str(temp_run_path)],
                        capture_output=True,
                        text=True,
                        timeout=90,
                        cwd=str(PROJECT_ROOT)
                    )
                    row_ok = (proc.returncode == 0)
                    if row_ok:
                        completed_rows += 1
                    else:
                        failed_rows += 1

                    record_logs.append({
                        "row": row_num,
                        "data": row,
                        "success": row_ok,
                        "output": proc.stdout[:300] if proc.stdout else "",
                        "error": proc.stderr[:300] if proc.stderr else None
                    })

                    if not row_ok and stop_on_error:
                        break
                finally:
                    if temp_run_path.exists():
                        try:
                            temp_run_path.unlink()
                        except Exception:
                            pass

                if delay_between_records_s > 0 and row_num < total_rows:
                    time.sleep(delay_between_records_s)

            return {
                "success": (failed_rows == 0),
                "workflow": clean_name,
                "total_rows": total_rows,
                "completed_rows": completed_rows,
                "failed_rows": failed_rows,
                "record_logs": record_logs
            }
        finally:
            self._is_running_workflow = False


# Singleton export
playwright_manager = PlaywrightManager.get_instance()
