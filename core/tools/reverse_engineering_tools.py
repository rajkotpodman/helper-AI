"""Reverse Engineering & App Knowledge Memory Tools for Helper-AI.

Gives agents the capability to reverse engineer any application, binary, or website,
persist and query app memory profiles, and execute 100% accurate fast-path automation.
"""

from typing import Dict, Any, Optional, List
from core.tools.base import BaseTool
from core.reverse_engineering.app_analyzer import ReverseEngineeringEngine
from core.reverse_engineering.app_memory_store import AppMemoryStore
from core.reverse_engineering.fast_operator import FastAppOperator
from core.reverse_engineering.rea_bridge import REABridge


class ReverseEngineerAppTool(BaseTool):
    """Deeply inspects and reverse engineers any application, binary, or website."""

    name = "reverse_engineer_app"
    description = (
        "Reverse engineers any desktop application (Win32, Electron, WPF, WinUI), executable file, "
        "running window, or website. Extracts UI automation controls, keyboard shortcuts, "
        "internal architecture, and IPC/APIs, and saves an AI-friendly profile to persistent "
        "AppMemoryStore so future operations are 100% accurate and instant without rediscovery."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Application name (e.g. 'Notepad', 'Slack', 'Spotify', 'Calculator'), process name ('code.exe'), file path ('C:\\Program Files\\...\\app.exe'), or URL ('https://...')."
            },
            "depth": {
                "type": "string",
                "description": "Analysis depth: 'quick' (UI tree + hotkeys), 'deep' (UI + architecture + package scan), or 'full_binary' (full REA decompilation/layout).",
                "enum": ["quick", "deep", "full_binary"],
                "default": "deep"
            },
            "save_to_memory": {
                "type": "boolean",
                "description": "Whether to save the reverse engineered profile into persistent AppMemoryStore and agent_memory.md (default: true).",
                "default": True
            }
        },
        "required": ["target"]
    }

    def execute(
        self,
        target: str,
        depth: str = "deep",
        save_to_memory: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        engine = ReverseEngineeringEngine.get_instance()
        return engine.reverse_engineer(target=target, depth=depth, save_to_memory=save_to_memory)


class QueryAppMemoryTool(BaseTool):
    """Retrieves remembered reverse-engineering profiles and fast-paths."""

    name = "query_app_memory"
    description = (
        "Queries persistent AppMemoryStore for known application profiles. "
        "Returns verified keyboard shortcuts, UI Automation control IDs, launch commands, "
        "and direct fast-paths so you can operate apps with 100% precision with 0 delay."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action: 'get' (retrieve profile for specific app), 'list' (list all remembered apps), 'search' (search by keyword).",
                "enum": ["get", "list", "search"],
                "default": "get"
            },
            "app_name": {
                "type": "string",
                "description": "Name, slug, or process of the app to query (e.g. 'Notepad', 'vscode', 'calc', 'chrome')."
            }
        },
        "required": ["action"]
    }

    def execute(
        self,
        action: str = "get",
        app_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        store = AppMemoryStore.get_instance()

        if action == "list":
            profiles = store.list_all_profiles()
            lines = [f"🧠 Stored Application Memory Profiles ({len(profiles)} total):"]
            for p in profiles:
                lines.append(
                    f"- 📦 **{p['app_name']}** (`{p['app_slug']}`): "
                    f"Type: {p['app_type']} | Shortcuts: {p['shortcuts_count']} | Controls: {p['controls_count']} | "
                    f"Launch: `{p['launch_command']}`"
                )
            return {
                "success": True,
                "profiles": profiles,
                "output": "\n".join(lines)
            }

        elif action in ["get", "search"]:
            if not app_name:
                return {"success": False, "error": "Please provide 'app_name' to query."}
            profile = store.get_app_profile(app_name)
            if not profile:
                profile = store.find_matching_profile_for_goal(app_name)

            if profile:
                prompt_text = store.format_for_ai_prompt(profile)
                return {
                    "success": True,
                    "profile": profile,
                    "output": f"Found remembered memory for '{profile.get('app_name')}':\n\n{prompt_text}"
                }
            else:
                return {
                    "success": False,
                    "output": f"No memory profile found for '{app_name}'. Use tool `reverse_engineer_app` to inspect and remember it automatically!"
                }

        return {"success": False, "error": f"Unknown action: {action}"}


class FastAppOperateTool(BaseTool):
    """Operates applications at maximum speed using reverse-engineered fast paths."""

    name = "fast_app_operate"
    description = (
        "Operates an application at maximum speed using reverse-engineered shortcuts, "
        "UI Automation direct controls, or launch commands with 100% accuracy. "
        "Avoids tedious screenshot-and-click loops by executing direct hotkeys (e.g. 'save', 'open', 'copy', 'paste', 'find', 'clear', 'equals') "
        "or setting control text directly."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Application name, slug, or process (e.g. 'Notepad', 'Calculator', 'vscode', 'chrome')."
            },
            "action": {
                "type": "string",
                "description": "Operation to perform: 'launch', 'hotkey', 'type', 'click_control', or shortcut names like 'save', 'open', 'new', 'find', 'copy', 'paste', 'clear', 'equals', 'select_all'."
            },
            "text": {
                "type": "string",
                "description": "Text to type into the active app, or custom hotkey keys (e.g. 'ctrl+s')."
            },
            "control_id": {
                "type": "string",
                "description": "AutomationId or Name of the control to invoke directly via UI Automation."
            }
        },
        "required": ["target", "action"]
    }

    def execute(
        self,
        target: str,
        action: str,
        text: Optional[str] = None,
        control_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        operator = FastAppOperator.get_instance()
        return operator.operate(app_target=target, action=action, text=text, control_id=control_id)


class McpReaCallTool(BaseTool):
    """Executes any tool from the connected REA (Reverse Engineer Anything) MCP server."""

    name = "mcp_rea_call"
    description = (
        "Directly invokes any of the 200+ specialized reverse engineering tools provided by REA "
        "(e.g. analyze_javascript_application, inspect_artifact, inspect_sqlite_database, search, trace, etc.)."
    )
    parameters = {
        "type": "object",
        "properties": {
            "tool_name": {
                "type": "string",
                "description": "Name of the REA MCP tool to invoke (e.g. 'analyze_javascript_application', 'inspect_artifact', 'inspect_sqlite_database', 'search', 'trace')."
            },
            "arguments": {
                "type": "object",
                "description": "Dictionary of arguments passed to the REA MCP tool.",
                "default": {}
            }
        },
        "required": ["tool_name"]
    }

    def execute(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        bridge = REABridge.get_instance()
        res = bridge.call_mcp_tool(tool_name, arguments or {})
        if res.get("success"):
            return {
                "success": True,
                "result": res.get("result"),
                "output": f"REA tool '{tool_name}' executed successfully:\n{json.dumps(res.get('result'), indent=2)[:2000]}"
            }
        else:
            return {
                "success": False,
                "error": res.get("error", "Unknown REA execution error"),
                "output": f"REA tool '{tool_name}' failed: {res.get('error')}"
            }
