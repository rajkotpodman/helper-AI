import asyncio
import json
import time
import logging
from typing import Callable, Optional, Dict, Any, List
from core.tools import ToolRegistry
from core.memory import AgentMemory, StepRecord
from core.llm import LLMClient
from core.audit import audit_logger
from core.metrics import metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HelperAgent")

class HelperAgent:
    """
    Autonomous AI agent designed to execute high-level goals on the user's PC
    and the internet without constant questioning.
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        tool_registry: Optional[ToolRegistry] = None,
        max_steps: int = 25,
        safe_mode: bool = False
    ):
        self.llm_client = llm_client or LLMClient()
        self.tools = tool_registry or ToolRegistry()
        self.max_steps = max_steps
        self.safe_mode = safe_mode
        self._is_running = False
        self._should_cancel = False

    def cancel(self):
        """Signals the agent to stop executing after the current step."""
        self._should_cancel = True
        logger.info("Agent received cancel signal.")

    async def run(
        self,
        goal: str,
        on_event: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Runs the autonomous goal execution loop.
        
        Args:
            goal: The high-level objective to achieve.
            on_event: Async or sync callback (event_type, event_data) for real-time UI/CLI streaming.
        """
        self._is_running = True
        memory = AgentMemory(goal)
        metrics.record_goal_start()

        def emit(event_type: str, data: Dict[str, Any]):
            if on_event:
                try:
                    if asyncio.iscoroutinefunction(on_event):
                        asyncio.create_task(on_event(event_type, data))
                    else:
                        on_event(event_type, data)
                except Exception as e:
                    logger.warning(f"Error in event listener: {e}")

        emit("started", {"goal": goal, "system_info": memory.system_info})
        tool_schemas_json = json.dumps(self.tools.get_schemas(), indent=2)

        final_message = ""
        success = False

        for step_idx in range(1, self.max_steps + 1):
            if self._should_cancel:
                emit("cancelled", {"message": "Goal was manually stopped by the user."})
                final_message = "Goal execution was cancelled by user request."
                metrics.record_goal_complete(success=False)
                break

            emit("step_start", {"step": step_idx, "max_steps": self.max_steps})

            # 1. Ask LLM for next thought & action
            trajectory = memory.get_trajectory_summary()
            step_decision = await asyncio.to_thread(
                self.llm_client.generate_step,
                goal=goal,
                trajectory_summary=trajectory,
                tool_schemas=tool_schemas_json,
                os_info=memory.system_info
            )

            thought = step_decision.get("thought", "")
            action = step_decision.get("action", "none")
            action_args = step_decision.get("action_args", {})
            is_complete = step_decision.get("is_complete", False)
            completion_msg = step_decision.get("completion_message", "")

            emit("thought", {
                "step": step_idx,
                "thought": thought,
                "action": action,
                "action_args": action_args
            })

            # 2. Check if goal was declared completed
            if is_complete or action == "none":
                success = True
                final_message = completion_msg or f"Goal '{goal}' has been completed successfully."
                metrics.record_goal_complete(success=True)
                emit("completed", {
                    "success": True,
                    "message": final_message,
                    "total_steps": step_idx
                })
                break

            # 3. Safety check for high-risk commands if Safe Mode is enabled
            if self.safe_mode and action == "execute_powershell":
                cmd = str(action_args.get("command", "")).lower()
                dangerous_patterns = ["rmdir /s", "del /f", "format ", "remove-item -recurse", "diskpart", "reg delete"]
                if any(p in cmd for p in dangerous_patterns):
                    obs = f"Action blocked by Safe Mode: dangerous command pattern detected in '{cmd}'."
                    memory.add_step(thought, action, action_args, obs, False)
                    audit_logger.log_event("tool_call_blocked", action, action_args, False, 0.0, obs, "SafeModeBlocked")
                    metrics.record_tool_call(action, False, 0.0)
                    emit("action_result", {"step": step_idx, "success": False, "output": obs})
                    continue

            # 4. Execute the chosen tool
            emit("action_executing", {"step": step_idx, "action": action, "action_args": action_args})
            t_start = time.time()
            tool_result = await asyncio.to_thread(self.tools.execute, action, action_args)
            duration_ms = (time.time() - t_start) * 1000

            action_success = tool_result.get("success", False)
            output_str = str(tool_result.get("output", ""))

            # Audit log and metrics recording
            audit_logger.log_event(
                event_type="tool_execution",
                action=action,
                arguments=action_args,
                success=action_success,
                duration_ms=duration_ms,
                output_snippet=output_str,
                error=tool_result.get("error")
            )
            metrics.record_tool_call(action, action_success, duration_ms)

            # 5. Record to memory
            memory.add_step(thought, action, action_args, output_str, action_success)

            emit("action_result", {
                "step": step_idx,
                "action": action,
                "success": action_success,
                "output": output_str
            })

            # Small delay to keep UI smooth
            await asyncio.sleep(0.3)
        else:
            final_message = f"Reached maximum allowed steps ({self.max_steps}) before goal was finalized."
            emit("completed", {
                "success": False,
                "message": final_message,
                "total_steps": self.max_steps
            })

        self._is_running = False
        return {
            "success": success,
            "goal": goal,
            "final_message": final_message,
            "steps_executed": len(memory.history),
            "history": [s.to_dict() for s in memory.history]
        }
