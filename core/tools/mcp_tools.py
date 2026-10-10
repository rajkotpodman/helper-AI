"""Model Context Protocol (MCP) Tool for Helper-AI.

Allows the agent to discover, inspect, and interact with open-source MCP servers and tools.
"""
from typing import Dict, Any, Optional, List
from core.tools.base import BaseTool
from core.mcp_manager import MCPManager


class MCPTool(BaseTool):
    """Discovers and coordinates Model Context Protocol (MCP) servers and tools."""
    name = "manage_mcp"
    description = (
        "Manages open-source Model Context Protocol (MCP) tools and servers. "
        "Allows Helper-AI to discover community tools (e.g. GitHub, Slack, SQLite, Google Drive, Filesystem) "
        "and list available external tools."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to perform: 'list_servers', 'list_tools', 'add_server', 'remove_server'",
                "enum": ["list_servers", "list_tools", "add_server", "remove_server"]
            },
            "name": {
                "type": "string",
                "description": "Name of the MCP server (e.g. 'github', 'sqlite', 'filesystem')."
            },
            "command": {
                "type": "string",
                "description": "Command to launch the MCP server (e.g. 'npx', 'python', 'uvx')."
            },
            "args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Arguments for the server launch command."
            },
            "description": {
                "type": "string",
                "description": "Short description of the MCP server."
            }
        },
        "required": ["action"]
    }

    def execute(
        self,
        action: str,
        name: Optional[str] = None,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        mgr = MCPManager.get_instance()

        if action == "list_servers":
            servers = mgr.list_servers()
            srv_list = "\n".join(f"- 🔌 **{s['name']}** ({s['command']}): {s['description']} [Enabled: {s['enabled']}]" for s in servers) or "No MCP servers configured."
            return {
                "success": True,
                "servers": servers,
                "output": f"Configured MCP Servers ({len(servers)} total):\n\n{srv_list}"
            }

        elif action == "list_tools":
            tools = mgr.list_tools_sync()
            tool_list = "\n".join(f"- 🛠️ **{t['name']}** ({t.get('server', '')}): {t.get('description', '')}" for t in tools) or "No external MCP tools currently active."
            return {
                "success": True,
                "tools": tools,
                "output": f"Discovered MCP Tools ({len(tools)} total):\n\n{tool_list}"
            }

        elif action == "add_server":
            if not name or not command:
                return {"success": False, "output": "Please provide both 'name' and 'command' to register an MCP server."}
            res = mgr.add_server(name, command, args or [], description or "")
            return {
                "success": True,
                "output": f"Successfully registered MCP server '{name}'. Command: {command} {' '.join(args or [])}",
                "server": res
            }

        elif action == "remove_server":
            if not name:
                return {"success": False, "output": "Please specify the server 'name' to remove."}
            res = mgr.remove_server(name)
            return {
                "success": res.get("success", False),
                "output": res.get("message", "")
            }

        else:
            return {
                "success": False,
                "output": f"Unknown MCP action: '{action}'. Available: list_servers, list_tools, add_server, remove_server."
            }
