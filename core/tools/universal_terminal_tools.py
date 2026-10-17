"""Universal Terminal & Cross-Platform Command Tools for Helper-AI.

Exposes high-power terminal execution, cross-platform command synthesis,
and community command recipe downloads to the agent and user.
"""

from typing import Dict, Any, Optional
from core.tools.base import BaseTool
from core.command_engine.os_detector import OSDetector
from core.command_engine.command_encyclopedia import CommandEncyclopedia
from core.command_engine.command_fetcher import CommandFetcher
from core.command_engine.executor import UniversalCommandExecutor
from core.command_engine.persistent_shell import PersistentShellManager


class UniversalTerminalTool(BaseTool):
    """Executes terminal commands on any operating system with stateful persistent shell and background capabilities."""

    name = "universal_terminal"
    description = (
        "Execute any terminal or PowerShell command on the host machine. "
        "Maintains a live, stateful interactive shell session (variables, directory changes, "
        "and virtual environments persist across steps). "
        "Supports long-running heavy background tasks with 'background: true', "
        "status checking with action='status', task cancellation with action='kill', "
        "and session management with action='reset_session' or action='session_info'."
    )
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The command line string to execute."
            },
            "action": {
                "type": "string",
                "enum": ["execute", "status", "kill", "reset_session", "session_info"],
                "default": "execute",
                "description": "Action to perform: 'execute' (run command), 'status' (check background task), 'kill' (stop task), 'reset_session' (restart shell), 'session_info' (view shell details)."
            },
            "persistent": {
                "type": "boolean",
                "default": True,
                "description": "If true (default), runs in persistent stateful shell preserving directory and variables across steps."
            },
            "session_id": {
                "type": "string",
                "default": "default",
                "description": "Identifier for the persistent shell session (default: 'default')."
            },
            "background": {
                "type": "boolean",
                "default": False,
                "description": "Set to true for heavy/long tasks that should run in the background."
            },
            "task_id": {
                "type": "string",
                "description": "Task identifier for checking status or terminating background execution."
            },
            "timeout_seconds": {
                "type": "integer",
                "default": 120,
                "description": "Maximum seconds to wait for execution."
            },
            "cwd": {
                "type": "string",
                "description": "Working directory in which to execute the command."
            }
        },
        "required": []
    }

    def execute(
        self,
        command: Optional[str] = None,
        action: str = "execute",
        persistent: bool = True,
        session_id: str = "default",
        background: bool = False,
        task_id: Optional[str] = None,
        timeout_seconds: int = 120,
        cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        if action == "reset_session":
            return PersistentShellManager.reset_session(session_id)

        if action == "session_info":
            sess = PersistentShellManager.get_session(session_id)
            return sess.get_info()

        if action == "status":
            if not task_id:
                return {"success": False, "error": "task_id is required for action='status'."}
            return UniversalCommandExecutor.get_task_status(task_id)

        if action == "kill":
            if not task_id:
                return {"success": False, "error": "task_id is required for action='kill'."}
            return UniversalCommandExecutor.kill_task(task_id)

        if not command:
            return {"success": False, "error": "command is required for action='execute'."}

        if background:
            return UniversalCommandExecutor.execute_background(command=command, cwd=cwd)

        # Stateful persistent shell execution (Open Interpreter style)
        if persistent:
            sess = PersistentShellManager.get_session(session_id)
            if cwd:
                # If explicit cwd provided, navigate to it in persistent shell
                sess.execute(f'cd "{cwd}"', timeout_seconds=10)
            return sess.execute(command, timeout_seconds=timeout_seconds)

        # Fallback to single-shot isolated execution
        return UniversalCommandExecutor.execute_sync(
            command=command,
            timeout_seconds=timeout_seconds,
            cwd=cwd
        )


class SynthesizeOSCommandTool(BaseTool):
    """Converts high-level goals into optimized native commands for any OS."""

    name = "synthesize_os_command"
    description = (
        "Translates high-level goals (e.g. 'kill process on port 8000', 'find large files', "
        "'check disk space', 'show listening ports') into exact, safe terminal commands for "
        "Windows PowerShell, Linux POSIX, or macOS."
    )
    parameters = {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "description": "High-level description of what you want to achieve."
            },
            "target_os": {
                "type": "string",
                "enum": ["auto", "windows", "linux", "macos"],
                "default": "auto",
                "description": "Target OS family. 'auto' detects the host system automatically."
            },
            "execute_now": {
                "type": "boolean",
                "default": False,
                "description": "If true, immediately executes the synthesized command on the host."
            }
        },
        "required": ["intent"]
    }

    def execute(
        self,
        intent: str,
        target_os: str = "auto",
        execute_now: bool = False
    ) -> Dict[str, Any]:
        if target_os == "auto":
            ctx = OSDetector.get_system_context()
            target_os = ctx["os"]["family"]

        recipe = CommandEncyclopedia.synthesize_for_intent(intent, target_os)
        if not recipe:
            return {
                "success": False,
                "intent": intent,
                "target_os": target_os,
                "error": f"No direct built-in recipe found for intent: '{intent}'. Use 'command_hub' to search or download cheatsheets."
            }

        response = {
            "success": True,
            "intent": intent,
            "target_os": target_os,
            "synthesized_command": recipe["command"],
            "shell_type": recipe["shell_type"],
            "description": recipe["description"]
        }

        if execute_now:
            exec_res = UniversalCommandExecutor.execute_sync(recipe["command"])
            response["execution_result"] = exec_res

        return response


class CommandHubTool(BaseTool):
    """Searches, downloads, and caches CLI cheat sheets and command recipes."""

    name = "command_hub"
    description = (
        "Downloads or retrieves cheat sheets, recipes, and manuals for any terminal command "
        "(e.g. ffmpeg, docker, tar, powershell, git, curl, iptables, systemctl). "
        "Pulls from community repositories (cheat.sh) and caches locally for offline use."
    )
    parameters = {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The command or tool name to fetch (e.g. 'ffmpeg', 'docker', 'tar', 'powershell')."
            },
            "action": {
                "type": "string",
                "enum": ["cheatsheet", "search", "list_all_recipes"],
                "default": "cheatsheet",
                "description": "Action: 'cheatsheet' (fetch full usage guide), 'search' (search built-in recipes), 'list_all_recipes' (list catalog)."
            },
            "force_refresh": {
                "type": "boolean",
                "default": False,
                "description": "Whether to bypass local cache and download fresh from web."
            }
        },
        "required": []
    }

    def execute(
        self,
        topic: Optional[str] = None,
        action: str = "cheatsheet",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        if action == "list_all_recipes":
            catalog = CommandEncyclopedia.get_catalog()
            return {
                "success": True,
                "total_recipes": len(catalog),
                "recipes": list(catalog.keys())
            }

        if action == "search":
            if not topic:
                return {"success": False, "error": "topic query is required for action='search'."}
            matches = CommandEncyclopedia.search_recipes(topic)
            return {
                "success": True,
                "query": topic,
                "match_count": len(matches),
                "matches": matches
            }

        # Default action: cheatsheet
        if not topic:
            return {"success": False, "error": "topic is required for action='cheatsheet'."}

        return CommandFetcher.fetch_command_cheatsheet(topic, force_refresh=force_refresh)
