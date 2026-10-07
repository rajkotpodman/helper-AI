"""Enterprise-grade Audit Logging and Security Monitoring for Helper-AI."""
import os
import re
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

SENSITIVE_PATTERNS = [
    r"AIza[0-9A-Za-z-_]{35}",           # Google API Key
    r"sk-[a-zA-Z0-9]{32,}",             # OpenAI API Key
    r"gsk_[a-zA-Z0-9]{32,}",            # Groq API Key
    r"gh[opsu]_[0-9a-zA-Z]{36,}",       # GitHub Token
    r"password\s*[:=]\s*['\"][^'\"]+",  # Generic Passwords
]

class AuditLogger:
    """
    Records every tool call, parameter set, and execution latency
    in structured JSON Lines format for compliance, debugging, and security audits.
    """
    def __init__(self, log_dir: Optional[str] = None):
        self.log_dir = Path(log_dir) if log_dir else (Path.cwd() / "logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.log_dir / "audit.jsonl"

    def _mask_sensitive_data(self, text: str) -> str:
        """Masks detected API keys and passwords from log files."""
        masked = text
        for pat in SENSITIVE_PATTERNS:
            masked = re.sub(pat, "[REDACTED_SECRET]", masked)
        return masked

    def log_event(
        self,
        event_type: str,
        action: str,
        arguments: Dict[str, Any],
        success: bool,
        duration_ms: float,
        output_snippet: str = "",
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Logs an action execution event with timing and status."""
        record = {
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event_type": event_type,
            "action": action,
            "arguments": arguments,
            "success": success,
            "duration_ms": round(duration_ms, 2),
            "output_snippet": output_snippet[:500] if output_snippet else "",
            "error": error
        }

        # Serialize and mask sensitive content
        serialized = json.dumps(record, default=str)
        safe_line = self._mask_sensitive_data(serialized)

        try:
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(safe_line + "\n")
        except Exception as e:
            logging.getLogger("AuditLogger").error(f"Failed to write audit log: {e}")

        return record

# Global singleton
audit_logger = AuditLogger()
