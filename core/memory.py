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

    def add_step(self, thought: str, action: str, action_args: Dict[str, Any], result: str, success: bool) -> StepRecord:
        step_num = len(self.history) + 1
        record = StepRecord(step_num, thought, action, action_args, result, success)
        self.history.append(record)
        return record

    def get_trajectory_summary(self, max_recent: int = 10) -> str:
        """Returns readable trajectory formatted for prompt context."""
        if not self.history:
            return "No previous steps executed yet."

        lines = []
        # If there are many steps, summarize earlier ones
        if len(self.history) > max_recent:
            lines.append(f"[{len(self.history) - max_recent} earlier steps succeeded. Showing the {max_recent} most recent steps:]")

        recent_steps = self.history[-max_recent:]
        for s in recent_steps:
            status = "SUCCESS" if s.success else "FAILED"
            # Truncate very long outputs in context
            res_snippet = s.result[:400] + ("..." if len(s.result) > 400 else "")
            lines.append(
                f"Step {s.step_number}:\n"
                f"  Thought: {s.thought}\n"
                f"  Action: {s.action} with arguments {json.dumps(s.action_args)}\n"
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
            "steps": [s.to_dict() for s in self.history]
        }, indent=2)
