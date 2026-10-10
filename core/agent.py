import asyncio
import json
import time
import logging
from typing import Callable, Optional, Dict, Any, List
from core.tools import ToolRegistry
from core.tools import ToolRegistry
from core.memory import AgentMemory, StepRecord
from core.llm import LLMClient
from core.audit import audit_logger
from core.metrics import metrics
from core.permissions import PermissionManager
from core.memory_recorder import MarkdownMemoryRecorder

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
        permission_manager: Optional[PermissionManager] = None,
        memory_recorder: Optional[MarkdownMemoryRecorder] = None,
        max_steps: int = 25,
        safe_mode: bool = False
    ):
        self.llm_client = llm_client or LLMClient()
        self.tools = tool_registry or ToolRegistry()
        self.permission_manager = permission_manager
        self.memory_recorder = memory_recorder or MarkdownMemoryRecorder()
        self.max_steps = max_steps
        self.safe_mode = safe_mode
        self._is_running = False
        self._should_cancel = False

    def cancel(self):
        """Signals the agent to stop executing after the current step."""
        self._should_cancel = True
        if self.permission_manager:
            self.permission_manager.cancel_all()
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
        tool_schemas_json = self.tools.get_concise_schema_text()

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
                # Prevent premature surrender when previous step failed
                if memory.history and not any(s.success for s in memory.history) and step_idx <= 3:
                    import re
                    p_match = re.search(r'([A-Za-z]:\\[^"\'\n\r;|]+)', goal)
                    if p_match and os.path.exists(p_match.group(1).strip()):
                        rescued_path = p_match.group(1).strip()
                        rescue_res = self.tools.execute("list_directory", {"path": rescued_path})
                        if rescue_res.get("success"):
                            memory.add_step(
                                "Autonomous Recovery: Rescued directory listing for requested path",
                                "list_directory",
                                {"path": rescued_path},
                                rescue_res.get("output", ""),
                                True
                            )
                            emit("action_result", {
                                "step": step_idx,
                                "action": "list_directory",
                                "success": True,
                                "output": rescue_res.get("output", "")
                            })
                            success = True
                            final_message = f"Successfully inspected '{rescued_path}':\n\n{rescue_res.get('output', '')}"
                            metrics.record_goal_complete(success=True)
                            emit("completed", {
                                "success": True,
                                "message": final_message,
                                "total_steps": step_idx
                            })
                            break

                has_succeeded = memory.history[-1].success if memory.history else True
                success = has_succeeded
                final_message = completion_msg or (
                    f"Goal '{goal}' has been completed successfully." if success else f"Goal '{goal}' could not be completed."
                )
                metrics.record_goal_complete(success=success)
                emit("completed", {
                    "success": success,
                    "message": final_message,
                    "total_steps": step_idx
                })
                break

            # 3. Permission & Safety check
            needs_permission = False
            perm_reason = ""
            if action == "execute_powershell":
                cmd = str(action_args.get("command", "")).lower()
                dangerous_patterns = ["rmdir /s", "del /f", "format ", "remove-item -recurse", "diskpart", "reg delete"]
                if any(p in cmd for p in dangerous_patterns):
                    needs_permission = True
                    perm_reason = f"High-risk terminal command detected: '{cmd}'"
            elif action == "browser_automation" and action_args.get("action") == "draft_social_post":
                needs_permission = True
                perm_reason = f"Social post publication to {action_args.get('platform', 'platform')}: \"{action_args.get('post_text', '')}\""

            if needs_permission:
                if self.permission_manager:
                    emit("permission_requested", {
                        "action": action,
                        "description": perm_reason,
                        "details": action_args
                    })
                    approved = await self.permission_manager.request_permission(
                        action=action,
                        description=perm_reason,
                        details=action_args
                    )
                    if not approved:
                        obs = f"Action blocked: user denied permission or request timed out ({perm_reason})."
                        memory.add_step(thought, action, action_args, obs, False)
                        audit_logger.log_event("tool_call_denied", action, action_args, False, 0.0, obs, "UserDenied")
                        metrics.record_tool_call(action, False, 0.0)
                        emit("action_result", {"step": step_idx, "success": False, "output": obs})
                        continue
                elif self.safe_mode:
                    obs = f"Action blocked by Safe Mode: {perm_reason}."
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

            # Fast-path early completion for successfully fulfilled single-intent goals
            lower_goal = goal.lower().strip()

            # A. App Launching (e.g. open/run/launch edge, chrome, notepad, calc, browser)
            if action == "open_app_or_file" and action_success:
                if any(w in lower_goal for w in ["open", "launch", "run", "start"]):
                    target_display = action_args.get("target") or action_args.get("app_name") or "Application"
                    success = True
                    final_message = f"Successfully launched '{target_display}'. The application is now open and active."
                    metrics.record_goal_complete(success=True)
                    emit("completed", {
                        "success": True,
                        "message": final_message,
                        "total_steps": step_idx
                    })
                    break

            # B. Ollama model query (e.g. check ollama models, which models installed)
            if action == "manage_ollama" and action_success:
                if any(w in lower_goal for w in ["which", "what", "check", "list", "installed", "status", "show", "running"]):
                    success = True
                    final_message = f"Ollama model status:\n\n{output_str}"
                    metrics.record_goal_complete(success=True)
                    emit("completed", {
                        "success": True,
                        "message": final_message,
                        "total_steps": step_idx
                    })
                    break

            # C. System Diagnostics (e.g. ram, cpu, health, specs)
            if action == "get_system_health" and action_success:
                if any(w in lower_goal for w in ["health", "specs", "ram", "cpu", "diagnostic", "hardware", "system info"]):
                    success = True
                    final_message = f"System Diagnostics:\n\n{output_str}"
                    metrics.record_goal_complete(success=True)
                    emit("completed", {
                        "success": True,
                        "message": final_message,
                        "total_steps": step_idx
                    })
                    break

            # D. Folder Inspection / File listing
            if action == "list_directory" and action_success:
                if any(w in lower_goal for w in ["check contents", "list files", "list contents", "show files", "what files", "see files", "show folder"]):
                    success = True
                    target_dir = action_args.get("path", "folder")
                    final_message = f"Contents of '{target_dir}':\n\n{output_str}"
                    metrics.record_goal_complete(success=True)
                    emit("completed", {
                        "success": True,
                        "message": final_message,
                        "total_steps": step_idx
                    })
                    break

            # E. Loop breaker: Stop execution if the same action fails 3 times consecutively
            if len(memory.history) >= 3:
                last_3 = memory.history[-3:]
                if all(not s.success and s.action == action for s in last_3):
                    success = False
                    final_message = f"Goal execution halted: Action '{action}' failed 3 consecutive times. Halting to avoid infinite loop."
                    metrics.record_goal_complete(success=False)
                    emit("completed", {
                        "success": False,
                        "message": final_message,
                        "total_steps": step_idx
                    })
                    break

            # Small delay to keep UI smooth
            await asyncio.sleep(0.3)
        else:
            final_message = f"Reached maximum allowed steps ({self.max_steps}) before goal was finalized."
            emit("completed", {
                "success": False,
                "message": final_message,
                "total_steps": self.max_steps
            })

        # Record interaction into markdown memory file
        mem_info = None
        if self.memory_recorder:
            try:
                mem_info = self.memory_recorder.record_interaction(
                    prompt=goal,
                    final_reply=final_message,
                    success=success,
                    steps_executed=len(memory.history)
                )
                if mem_info.get("limit_reached"):
                    emit("memory_limit_reached", mem_info)
                    logger.warning(mem_info.get("alert_message", ""))
            except Exception as e:
                logger.warning(f"Error recording interaction to memory file: {e}")

        self._is_running = False
        return {
            "success": success,
            "goal": goal,
            "final_message": final_message,
            "steps_executed": len(memory.history),
            "memory_info": mem_info,
            "history": [s.to_dict() for s in memory.history]
        }
