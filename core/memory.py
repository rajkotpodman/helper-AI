"""Memory and context management for Helper-AI."""
import os
import json
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional

class StepRecord:
    def __init__(self, step_number: int, thought: str, action: str, action_args: Dict[str, Any], result: str, success: bool):
        self.step_number = step_number
        self.thought = thought
        self.action = action
        self.action_args = action_args
        self.result = result
        self.success = success

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "thought": self.thought,
            "action": self.action,
            "action_args": self.action_args,
            "result": self.result,
            "success": self.success
        }


class AgentMemory:
    """Stores execution history, context, and plan progress for an agent goal."""

    def __init__(self, goal: str):
        self.goal = goal
        self.history: List[StepRecord] = []
        self.pinned_facts: List[str] = []
        self.scratchpad: Dict[str, Any] = {}
        self.milestones: List[Dict[str, Any]] = []
        home = Path.home()
        desktop_dir = home / "OneDrive" / "Desktop" if (home / "OneDrive" / "Desktop").exists() else home / "Desktop"
        self.system_info = {
            "os": platform.system(),
            "release": platform.release(),
            "cwd": str(Path.cwd()),
            "user_home": str(home),
            "desktop": str(desktop_dir),
            "downloads": str(home / "Downloads")
        }

    def pin_fact(self, fact: str):
        """Pins a critical discovery or fact so it is never dropped from agent context."""
        fact_str = fact.strip()
        if fact_str and fact_str not in self.pinned_facts:
            self.pinned_facts.append(fact_str)

    def set_milestones(self, milestones: List[Dict[str, Any]]):
        """Sets high-level plan milestones for multi-phase tasks."""
        self.milestones = milestones

    def update_milestone(self, index: int, status: str):
        """Updates the status of a specific milestone ('pending', 'in_progress', 'completed')."""
        if 0 <= index < len(self.milestones):
            self.milestones[index]["status"] = status

    def add_step(self, thought: str, action: str, action_args: Dict[str, Any], result: str, success: bool) -> StepRecord:
        step_num = len(self.history) + 1
        record = StepRecord(step_num, thought, action, action_args, result, success)
        self.history.append(record)

        # Auto-pin high-value discoveries (e.g. newly created files, downloaded files, repo details)
        if success and result:
            import re
            file_match = re.search(r'(?:saved|created|written|downloaded|output) (?:to|at|file)\s+([A-Za-z]:\\[^\s\n\r"\'<>]+|\b[A-Za-z0-9_\-\./\\]+\.[a-zA-Z0-9]{2,5}\b)', result, re.IGNORECASE)
            if file_match:
                self.pin_fact(f"Created/Accessed Asset: {file_match.group(1)}")

        return record

    def get_trajectory_summary(self, max_recent: int = 12) -> str:
        """Returns readable trajectory formatted for prompt context with pinned facts preservation."""
        if not self.history and not self.pinned_facts:
            return "No previous steps executed yet."

        lines = []

        # 1. Pinned facts & persistent discoveries
        if self.pinned_facts:
            lines.append("📌 CRITICAL PINNED FACTS & DISCOVERIES (Retained across all steps):")
            for fact in self.pinned_facts[-10:]:
                lines.append(f"  • {fact}")
            lines.append("")

        # 2. Milestones progress if defined
        if self.milestones:
            lines.append("🗺️ ACTIVE TASK MILESTONES:")
            for idx, m in enumerate(self.milestones, start=1):
                icon = "✅" if m.get("status") == "completed" else ("🔄" if m.get("status") == "in_progress" else "⏳")
                lines.append(f"  {icon} Phase {idx}: {m.get('title', 'Phase')} [{m.get('status', 'pending')}]")
            lines.append("")

        # 3. Trajectory history
        if len(self.history) > max_recent:
            lines.append(f"[{len(self.history) - max_recent} earlier steps succeeded. Showing the {max_recent} most recent steps:]")

        recent_steps = self.history[-max_recent:]
        for idx, s in enumerate(recent_steps):
            is_latest = (idx == len(recent_steps) - 1)
            status = "SUCCESS" if s.success else "FAILED"
            # For the most recent step, provide generous context budget (up to 20,000 chars)
            # so the model can inspect complete data sets, full source files, or crawling results.
            # For older steps, provide up to 3,500 chars.
            char_limit = 20000 if is_latest else 3500
            if len(s.result) <= char_limit:
                res_snippet = s.result
            else:
                res_snippet = s.result[:char_limit] + f"\n... [Truncated {len(s.result) - char_limit} chars; showing first {char_limit} chars of {len(s.result)} total]"

            # Safely truncate abnormally massive argument strings to protect token limits
            safe_args = {}
            for k, v in (s.action_args or {}).items():
                if isinstance(v, str) and len(v) > 1500:
                    safe_args[k] = v[:1500] + f"... [truncated {len(v)} chars]"
                else:
                    safe_args[k] = v

            lines.append(
                f"Step {s.step_number}:\n"
                f"  Thought: {s.thought}\n"
                f"  Action: {s.action} with arguments {json.dumps(safe_args)}\n"
                f"  Observation ({status}): {res_snippet}\n"
            )

        # Anti-loop warning for small models
        if len(self.history) >= 2:
            last1 = self.history[-1]
            last2 = self.history[-2]
            if not last1.success and not last2.success and last1.action == last2.action:
                lines.append(
                    f"\n⚠️ CRITICAL WARNING: Action '{last1.action}' has failed consecutively! "
                    "DO NOT repeat this failing action or similar command. You must pivot to an alternative tool or command immediately."
                )

        return "\n".join(lines)

    def export_json(self) -> str:
        return json.dumps({
            "goal": self.goal,
            "pinned_facts": self.pinned_facts,
            "milestones": self.milestones,
            "steps": [s.to_dict() for s in self.history]
        }, indent=2)
