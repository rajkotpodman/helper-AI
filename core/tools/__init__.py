"""Tools Registry for Helper-AI"""
from typing import Dict, List, Any
from core.tools.base import BaseTool
from core.tools.system_tools import (
    ExecutePowerShellTool,
    GetSystemHealthTool,
    ProcessManagerTool,
    OpenAppOrFileTool,
    ManageOllamaTool
)
from core.tools.file_tools import (
    ListDirectoryTool,
    ReadFileTool,
    WriteFileTool,
    MoveOrCopyFileTool,
    SearchFilesTool
)
from core.tools.web_tools import (
    SearchWebTool,
    FetchWebContentTool,
    DownloadFileTool
)
from core.tools.browser_tools import BrowserAutomationTool

class ToolRegistry:
    """Central registry of all tools available to Helper-AI."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def _register_default_tools(self):
        defaults = [
            ManageOllamaTool(),
            GetSystemHealthTool(),
            ProcessManagerTool(),
            ListDirectoryTool(),
            ReadFileTool(),
            WriteFileTool(),
            MoveOrCopyFileTool(),
            SearchFilesTool(),
            SearchWebTool(),
            FetchWebContentTool(),
            DownloadFileTool(),
            OpenAppOrFileTool(),
            BrowserAutomationTool(),
            ExecutePowerShellTool()
        ]
        for t in defaults:
            self.register(t)

    def get_tool(self, name: str) -> BaseTool:
        return self._tools.get(name)

    def get_all_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    def get_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_schema() for tool in self._tools.values()]

    def get_concise_schema_text(self) -> str:
        lines = []
        for t in self.get_all_tools():
            props = t.parameters.get("properties", {})
            params = ", ".join(props.keys())
            lines.append(f"- {t.name}({params}): {t.description}")
        return "\n".join(lines)

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "output": f"Unknown tool: '{tool_name}'. Available tools: {list(self._tools.keys())}",
                "error": "ToolNotFound"
            }
        try:
            return tool.execute(**arguments)
        except Exception as e:
            return {
                "success": False,
                "output": f"Tool '{tool_name}' execution crashed: {str(e)}",
                "error": str(e)
            }
