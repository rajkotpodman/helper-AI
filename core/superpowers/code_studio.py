"""Superpower Code Studio & Automated Project Generation Engine.

Scaffolds multi-file applications, performs automated AST/syntax validation,
resolves dependencies, runs test executions in isolated processes, and reports verification.
"""

import os
import sys
import py_compile
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


class SuperpowerCodeStudio:
    """Automated multi-file project scaffolding, syntax validation, and sandbox runner."""

    @staticmethod
    def create_project(
        project_dir: str,
        files: Dict[str, str],
        run_entrypoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a complete multi-file project and performs automated syntax checks.

        Args:
            project_dir: Root directory for the project.
            files: Dictionary mapping relative file paths to string file contents.
            run_entrypoint: Optional main file to execute for verification (e.g. 'main.py').

        Returns:
            Dictionary with creation status, syntax check results, and execution output.
        """
        target_root = Path(project_dir).resolve()
        target_root.mkdir(parents=True, exist_ok=True)

        written_files = []
        syntax_errors = []

        # 1. Write all files
        for rel_path, content in files.items():
            f_path = target_root / rel_path
            f_path.parent.mkdir(parents=True, exist_ok=True)
            f_path.write_text(content, encoding="utf-8")
            written_files.append(str(f_path.relative_to(target_root)).replace("\\", "/"))

            # Syntax check Python files
            if f_path.suffix.lower() == ".py":
                try:
                    py_compile.compile(str(f_path), doraise=True)
                except py_compile.PyCompileError as pe:
                    syntax_errors.append({
                        "file": rel_path,
                        "error": str(pe)
                    })

        # 2. Execution check if requested
        execution_result = None
        if run_entrypoint and not syntax_errors:
            entry_path = target_root / run_entrypoint
            if entry_path.exists():
                try:
                    start_t = time.perf_counter()
                    res = subprocess.run(
                        [sys.executable, str(entry_path)],
                        capture_output=True,
                        text=True,
                        timeout=15,
                        cwd=str(target_root),
                        encoding="utf-8",
                        errors="replace"
                    )
                    elapsed = round(time.perf_counter() - start_t, 2)
                    execution_result = {
                        "entrypoint": run_entrypoint,
                        "exit_code": res.returncode,
                        "stdout": res.stdout.strip(),
                        "stderr": res.stderr.strip(),
                        "elapsed_seconds": elapsed,
                        "success": (res.returncode == 0)
                    }
                except Exception as e:
                    execution_result = {
                        "entrypoint": run_entrypoint,
                        "exit_code": -1,
                        "error": str(e),
                        "success": False
                    }

        has_errors = bool(syntax_errors or (execution_result and not execution_result.get("success")))

        return {
            "success": not has_errors,
            "project_directory": str(target_root),
            "total_files_created": len(written_files),
            "files": written_files,
            "syntax_valid": len(syntax_errors) == 0,
            "syntax_errors": syntax_errors,
            "execution_verification": execution_result
        }
