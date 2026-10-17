"""REA (Reverse Engineer Anything) Bridge for Helper-AI.

Provides high-speed interfaces to REA's CLI and Model Context Protocol (MCP) server.
Allows Helper-AI agents to dissect binaries, inspect Electron/JavaScript packages,
analyze network traffic, read database schemas, and trace runtime execution.
Supports both local compiled REA installations and dynamic portable npx fallback.
"""

import os
import sys
import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("REABridge")

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
REA_SCRIPT = WORKSPACE_DIR / "rea_repo" / "scripts" / "rea.mjs"


class REABridge:
    """Interface to REA's CLI and MCP tools."""
    
    _instance: Optional["REABridge"] = None
    _cached_tools: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def get_instance(cls) -> "REABridge":
        if cls._instance is None:
            cls._instance = REABridge()
        return cls._instance

    def __init__(self, script_path: Optional[Path] = None):
        self.script_path = Path(script_path or REA_SCRIPT)
        self.node_executable = "node"

    def _get_launch_prefix(self) -> List[str]:
        """Returns local node command if local compiled script exists, else npx runner."""
        if self.script_path.exists():
            return [self.node_executable, str(self.script_path)]
        if shutil.which("rea"):
            return ["rea"]
        return ["npx", "-y", "rea-agents@latest"]

    def is_available(self) -> bool:
        """Returns True if REA CLI is installed, compiled, or runnable via npx."""
        prefix = self._get_launch_prefix()
        try:
            res = subprocess.run(
                prefix + ["--version"],
                capture_output=True,
                text=True,
                timeout=8
            )
            return res.returncode == 0
        except Exception as e:
            logger.warning(f"REA availability check failed: {e}")
            return False

    def get_version(self) -> str:
        """Returns REA version string."""
        prefix = self._get_launch_prefix()
        try:
            res = subprocess.run(
                prefix + ["--version"],
                capture_output=True,
                text=True,
                timeout=8
            )
            return res.stdout.strip() if res.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def execute_cli(
        self,
        command: str,
        args: Optional[List[str]] = None,
        json_format: bool = True,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Executes a REA CLI command and returns parsed JSON or text output.
        """
        prefix = self._get_launch_prefix()
        cmd_list = list(prefix) + [command]
        if args:
            cmd_list.extend(args)
        if json_format and "--format" not in cmd_list:
            cmd_list.extend(["--format", "json"])

        try:
            res = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            stdout = res.stdout.strip()
            stderr = res.stderr.strip()

            if res.returncode == 0:
                if json_format:
                    try:
                        parsed = json.loads(stdout)
                        return {"success": True, "data": parsed, "raw": stdout}
                    except json.JSONDecodeError:
                        return {"success": True, "raw": stdout}
                return {"success": True, "output": stdout}
            else:
                return {
                    "success": False,
                    "error": stderr or stdout or f"Exited with code {res.returncode}",
                    "returncode": res.returncode
                }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"REA command '{command}' timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def call_mcp_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Calls any of REA's 200+ MCP tools via standard JSON-RPC stdio.
        """
        arguments = arguments or {}
        prefix = self._get_launch_prefix()

        init_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "HelperAI-REABridge", "version": "1.0"}
            }
        }) + "\n"
        notif_req = json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }) + "\n"
        call_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }) + "\n"

        payload = init_req + notif_req + call_req

        try:
            p = subprocess.Popen(
                prefix + ["--mcp"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = p.communicate(payload, timeout=timeout)
            
            # Find JSON line corresponding to response id 2
            for line in stdout.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    if msg.get("id") == 2:
                        if "error" in msg:
                            return {"success": False, "error": msg["error"]}
                        return {"success": True, "result": msg.get("result", {})}
                except json.JSONDecodeError:
                    continue

            return {"success": False, "error": "No response for tools/call request", "raw": stdout}
        except subprocess.TimeoutExpired:
            p.kill()
            return {"success": False, "error": f"MCP tool '{tool_name}' call timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_mcp_tools(self, timeout: int = 15) -> List[Dict[str, Any]]:
        """Lists all advertised REA MCP tools."""
        if self._cached_tools is not None:
            return self._cached_tools

        prefix = self._get_launch_prefix()

        init_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "HelperAI-REABridge", "version": "1.0"}
            }
        }) + "\n"
        notif_req = json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }) + "\n"
        list_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }) + "\n"

        payload = init_req + notif_req + list_req

        try:
            p = subprocess.Popen(
                prefix + ["--mcp"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, _ = p.communicate(payload, timeout=timeout)
            for line in stdout.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    if msg.get("id") == 2 and "result" in msg and "tools" in msg["result"]:
                        self._cached_tools = msg["result"]["tools"]
                        return self._cached_tools
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.warning(f"Failed to list REA MCP tools: {e}")

        return []
