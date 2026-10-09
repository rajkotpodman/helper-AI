"""Persistent Markdown Memory Recorder for Helper-AI.

Records all user prompts (goals) and their final agent replies into a simple
markdown file (`agent_memory.md`). When the file reaches 20 MB, it alerts the
user to copy and store the file, archives/clears the file, and starts a fresh
20 MB memory log for the AI agent.
"""

import os
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger("MemoryRecorder")

DEFAULT_MEMORY_FILE = Path("agent_memory.md")
DEFAULT_MAX_BYTES = 20 * 1024 * 1024  # 20 MB (20,971,520 bytes)


class MarkdownMemoryRecorder:
    """Manages persistent logging of prompts and final replies to a markdown memory file."""

    def __init__(
        self,
        file_path: Optional[Path] = None,
        max_bytes: int = DEFAULT_MAX_BYTES
    ):
        self.file_path = Path(file_path or DEFAULT_MEMORY_FILE)
        self.max_bytes = max_bytes
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Initializes the memory file with a clean markdown header if not present."""
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            self._init_file()

    def _init_file(self):
        """Creates or resets the markdown file with a clean header."""
        header = (
            "# 🧠 Helper-AI Memory Log\n\n"
            "*Persistent record of all user prompts and final agent replies.*\n\n"
            "---\n\n"
        )
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(header)

    def get_size_bytes(self) -> int:
        """Returns the current size of the memory file in bytes."""
        if not self.file_path.exists():
            return 0
        return self.file_path.stat().st_size

    def get_size_mb(self) -> float:
        """Returns the current size in megabytes (MB)."""
        return round(self.get_size_bytes() / (1024 * 1024), 2)

    def is_limit_reached(self) -> bool:
        """Checks if the file has reached or exceeded max_bytes (20 MB default)."""
        return self.get_size_bytes() >= self.max_bytes

    def record_interaction(
        self,
        prompt: str,
        final_reply: str,
        success: bool = True,
        steps_executed: int = 0
    ) -> Dict[str, Any]:
        """
        Appends prompt and final reply to the markdown memory file.
        Checks if file size reached the 20 MB limit.
        If limit is reached:
          - Generates user alert asking to copy and store the file.
          - Archives and clears all contents from the file.
          - Starts a fresh 20 MB memory cycle.
        """
        self._ensure_file_exists()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_text = "✅ SUCCESS" if success else "❌ FAILED / INCOMPLETE"

        entry = (
            f"## 🎯 Prompt [{timestamp}]\n\n"
            f"> **User Prompt / Goal:** {prompt.strip()}\n\n"
            f"- **Execution Status:** {status_text}\n"
            f"- **Steps Executed:** {steps_executed}\n\n"
            f"### 💬 Final Reply:\n\n"
            f"{final_reply.strip()}\n\n"
            f"---\n\n"
        )

        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(entry)

        current_size = self.get_size_bytes()
        limit_reached = current_size >= self.max_bytes
        alert_message = ""
        archive_path_str = None

        if limit_reached:
            # Generate clear alert message for the user
            alert_message = (
                f"⚠️ Memory Alert: Your AI agent memory file '{self.file_path.name}' has reached 20 MB! "
                f"Please copy and store/backup the file. "
                f"All contents have been archived and reset to start a fresh 20 MB memory file."
            )
            logger.warning(alert_message)

            # Preserve backup archive before wiping
            archive_file = self.file_path.with_name(
                f"{self.file_path.stem}_backup_{int(time.time())}.md"
            )
            try:
                shutil.copy2(self.file_path, archive_file)
                archive_path_str = str(archive_file)
            except Exception as e:
                logger.warning(f"Could not create archive copy: {e}")

            # Delete all from file and start new 20 MB memory file
            self._init_file()

        return {
            "recorded": True,
            "timestamp": timestamp,
            "file_path": str(self.file_path),
            "size_bytes": self.get_size_bytes(),
            "size_mb": self.get_size_mb(),
            "limit_reached": limit_reached,
            "alert_message": alert_message,
            "archive_path": archive_path_str
        }

    def reset_file(self) -> None:
        """Empties all contents from the file and initializes a fresh header."""
        self._init_file()

    def read_content(self) -> str:
        """Reads the entire content of the markdown memory file."""
        if not self.file_path.exists():
            return ""
        with open(self.file_path, "r", encoding="utf-8") as f:
            return f.read()
