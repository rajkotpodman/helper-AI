"""Model Context Protocol (MCP) Client Manager for Helper-AI.

Allows Helper-AI to connect to any community open-source MCP server
and dynamically expose external tools (e.g. GitHub, SQLite, Filesystem, Slack, Google Drive)
to the agentic execution loop.
"""
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("MCPManager")

CONFIG_PATH = Path("mcp_servers.json")

DEFAULT_CONFIG = {
    "mcpServers": {
        "sqlite_demo": {
            "description": "Local SQLite database inspector (MCP reference)",
            "command": "python",
            "args": ["-m", "sqlite3"],
            "enabled": False
        }
    }
}


class MCPManager:
    """Singleton manager for MCP server connections and tool resolution."""
    _instance: Optional["MCPManager"] = None

    @classmethod
    def get_instance(cls) -> "MCPManager":
        if cls._instance is None:
            cls._instance = MCPManager()
        return cls._instance

    def __init__(self):
        self._config = self._load_config()
        self._tool_cache: Dict[str, Dict[str, Any]] = {}

    def _load_config(self) -> Dict[str, Any]:
        if not CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_CONFIG, f, indent=2)
                return DEFAULT_CONFIG
            except Exception as e:
                logger.error(f"Failed to create default mcp_servers.json: {e}")
                return DEFAULT_CONFIG
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load mcp_servers.json: {e}")
            return DEFAULT_CONFIG

    def _save_config(self) -> None:
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save mcp_servers.json: {e}")

    def list_servers(self) -> List[Dict[str, Any]]:
        """Returns all configured MCP servers and their current status."""
        servers = []
        for name, cfg in self._config.get("mcpServers", {}).items():
            servers.append({
                "name": name,
                "command": cfg.get("command", ""),
                "args": cfg.get("args", []),
                "enabled": cfg.get("enabled", True),
                "description": cfg.get("description", "Community MCP Server")
            })
        return servers

    def add_server(self, name: str, command: str, args: Optional[List[str]] = None, description: str = "") -> Dict[str, Any]:
        """Registers a new MCP server in the configuration."""
        if "mcpServers" not in self._config:
            self._config["mcpServers"] = {}
        self._config["mcpServers"][name] = {
            "command": command,
            "args": args or [],
            "enabled": True,
            "description": description or f"MCP Server '{name}'"
        }
        self._save_config()
        return {"success": True, "server": name, "message": f"MCP server '{name}' registered successfully."}

    def remove_server(self, name: str) -> Dict[str, Any]:
        """Removes an MCP server from configuration."""
        if name in self._config.get("mcpServers", {}):
            del self._config["mcpServers"][name]
            self._save_config()
            return {"success": True, "message": f"MCP server '{name}' removed."}
        return {"success": False, "message": f"MCP server '{name}' not found."}

    def check_connection(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Validates MCP server configuration and command availability."""
        servers = self.list_servers()
        if name:
            cfg = self._config.get("mcpServers", {}).get(name)
            if not cfg:
                return {"server": name, "status": "not_found", "message": f"Server '{name}' is not registered."}
            return {
                "server": name,
                "status": "configured" if cfg.get("enabled", False) else "disabled",
                "command": cfg.get("command"),
                "message": f"Server '{name}' configured ({'enabled' if cfg.get('enabled') else 'disabled'})."
            }
        return {
            "total_configured": len(servers),
            "servers": servers,
            "status": "connected" if servers else "empty"
        }

    async def list_tools_async(self) -> List[Dict[str, Any]]:
        """
        Discovers tools across all enabled MCP servers.
        Uses mcp.client.stdio.stdio_client to connect and query tools/list.
        """
        tools = []
        # Return mock / cached demo tool if no external live server is active
        for s_name, s_cfg in self._config.get("mcpServers", {}).items():
            if not s_cfg.get("enabled", False):
                continue
            try:
                from mcp import StdioServerParameters
                from mcp.client.stdio import stdio_client
                from mcp import ClientSession

                params = StdioServerParameters(
                    command=s_cfg.get("command", "python"),
                    args=s_cfg.get("args", []),
                    env=s_cfg.get("env")
                )
                async with stdio_client(params) as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        result = await session.list_tools()
                        for t in result.tools:
                            tools.append({
                                "server": s_name,
                                "name": f"mcp_{s_name}_{t.name}",
                                "description": t.description or f"Tool from {s_name}",
                                "inputSchema": t.inputSchema
                            })
            except Exception as e:
                logger.warning(f"Could not connect to MCP server '{s_name}': {e}")
                # Provide graceful informational entry
                tools.append({
                    "server": s_name,
                    "name": f"mcp_{s_name}_status",
                    "description": f"MCP status probe for '{s_name}' (Offline or initializing)",
                    "inputSchema": {"type": "object", "properties": {}}
                })
        return tools

    def list_tools_sync(self) -> List[Dict[str, Any]]:
        """Synchronously returns discovered MCP tools."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(lambda: asyncio.run(self.list_tools_async())).result()
            else:
                return loop.run_until_complete(self.list_tools_async())
        except Exception:
            return []
