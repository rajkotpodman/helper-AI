"""Local Configuration & File Integrity Monitoring (FIM) Engine.

Computes cryptographic SHA-256 hash baselines to detect unauthorized
file modifications, additions, or deletions across target system directories.
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


class FileIntegrityChecker:
    """File Integrity Monitor using SHA-256 cryptographic hashing."""

    CHUNK_SIZE = 65536  # 64 KB read chunks for memory-efficient hashing

    @staticmethod
    def calculate_file_hash(filepath: Path) -> Optional[str]:
        """Calculates SHA-256 hash for a given file."""
        sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(FileIntegrityChecker.CHUNK_SIZE):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (PermissionError, FileNotFoundError, OSError):
            return None

    def create_baseline(
        self,
        directory: str,
        baseline_file: str,
        exclude_extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generates and saves a cryptographic baseline snapshot of a target directory.

        Args:
            directory: Directory to monitor.
            baseline_file: Output path to save the JSON baseline.
            exclude_extensions: File extensions to skip (e.g. ['.tmp', '.log']).

        Returns:
            Dictionary containing summary metrics and file inventory.
        """
        target_dir = Path(directory).resolve()
        if not target_dir.exists() or not target_dir.is_dir():
            return {
                "success": False,
                "error": f"Directory does not exist: {directory}"
            }

        excludes = set(ext.lower() for ext in (exclude_extensions or []))
        files_catalog: Dict[str, Dict[str, Any]] = {}
        total_bytes = 0

        for root, _, files in os.walk(target_dir):
            for filename in files:
                f_path = Path(root) / filename
                if f_path.suffix.lower() in excludes:
                    continue

                rel_path = str(f_path.relative_to(target_dir)).replace("\\", "/")
                file_hash = self.calculate_file_hash(f_path)
                if file_hash:
                    try:
                        stat = f_path.stat()
                        files_catalog[rel_path] = {
                            "hash": file_hash,
                            "size": stat.st_size,
                            "modified_timestamp": stat.st_mtime
                        }
                        total_bytes += stat.st_size
                    except OSError:
                        pass

        snapshot = {
            "version": "1.0",
            "created_at": time.time(),
            "target_directory": str(target_dir),
            "file_count": len(files_catalog),
            "total_bytes": total_bytes,
            "files": files_catalog
        }

        baseline_out = Path(baseline_file).resolve()
        baseline_out.parent.mkdir(parents=True, exist_ok=True)
        with open(baseline_out, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)

        return {
            "success": True,
            "baseline_path": str(baseline_out),
            "target_directory": str(target_dir),
            "files_indexed": len(files_catalog),
            "total_bytes": total_bytes
        }

    def verify_integrity(
        self,
        directory: str,
        baseline_file: str
    ) -> Dict[str, Any]:
        """
        Compares the current directory state against a pre-established baseline.

        Args:
            directory: Directory to audit.
            baseline_file: Path to the pre-generated baseline JSON.

        Returns:
            Dictionary identifying modified, added, deleted, and untouched files.
        """
        target_dir = Path(directory).resolve()
        baseline_in = Path(baseline_file).resolve()

        if not baseline_in.exists():
            return {
                "success": False,
                "error": f"Baseline file not found: {baseline_file}"
            }

        try:
            with open(baseline_in, "r", encoding="utf-8") as f:
                baseline_data = json.load(f)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse baseline file: {str(e)}"
            }

        expected_files = baseline_data.get("files", {})

        # Scan current directory
        current_files: Dict[str, str] = {}
        for root, _, files in os.walk(target_dir):
            for filename in files:
                f_path = Path(root) / filename
                rel_path = str(f_path.relative_to(target_dir)).replace("\\", "/")
                file_hash = self.calculate_file_hash(f_path)
                if file_hash:
                    current_files[rel_path] = file_hash

        modified: List[Dict[str, str]] = []
        unmodified: List[str] = []
        deleted: List[str] = []
        added: List[str] = []

        # Check existing files vs baseline
        for rel_path, exp_info in expected_files.items():
            if rel_path in current_files:
                if current_files[rel_path] == exp_info["hash"]:
                    unmodified.append(rel_path)
                else:
                    modified.append({
                        "file": rel_path,
                        "expected_hash": exp_info["hash"],
                        "current_hash": current_files[rel_path]
                    })
            else:
                deleted.append(rel_path)

        # Detect newly added files
        for rel_path in current_files:
            if rel_path not in expected_files:
                added.append(rel_path)

        has_violations = bool(modified or deleted or added)
        status = "COMPROMISED / DRIFTED" if has_violations else "INTACT / VERIFIED"

        return {
            "success": True,
            "status": status,
            "has_violations": has_violations,
            "baseline_date": baseline_data.get("created_at"),
            "total_baseline_files": len(expected_files),
            "unmodified_count": len(unmodified),
            "modified_count": len(modified),
            "added_count": len(added),
            "deleted_count": len(deleted),
            "modified_files": modified,
            "added_files": added,
            "deleted_files": deleted
        }
