"""Comprehensive tests for the 4 open-source integrated phases in Helper-AI:
Phase 1: Edge-TTS Voice Engine & Speech Tool
Phase 2: Playwright Vision Browser Tool
Phase 3: Model Context Protocol (MCP) Manager & Tool
Phase 4: Native Desktop GUI Control Tool (PyAutoGUI + PyWinAuto)
"""
import pytest
from core.tools import ToolRegistry
from core.voice_engine import VoiceEngine
from core.tools.voice_tools import VoiceSpeechTool
from core.tools.playwright_tools import VisionBrowserTool
from core.mcp_manager import MCPManager
from core.tools.mcp_tools import MCPTool
from core.tools.desktop_gui_tools import DesktopGUIControlTool


def test_registry_has_18_tools():
    """Verify ToolRegistry loaded all 18 tools (14 original + 4 new open-source phases)."""
    registry = ToolRegistry()
    tools = registry.get_all_tools()
    tool_names = [t.name for t in tools]
    assert len(tools) >= 18
    assert "check_connections" in tool_names
    assert "speak_aloud" in tool_names
    assert "vision_browser" in tool_names
    assert "manage_mcp" in tool_names
    assert "desktop_gui_control" in tool_names


# ==================== PHASE 1: VOICE ENGINE TESTS ====================

def test_voice_engine_voices_list():
    voices = VoiceEngine.list_voices()
    assert len(voices) >= 4
    assert any("Aria" in v["name"] for v in voices)

def test_voice_speech_tool_execution(monkeypatch):
    tool = VoiceSpeechTool()
    schema = tool.to_schema()
    assert schema["name"] == "speak_aloud"
    assert "text" in schema["parameters"]["properties"]

    # Mock speak_on_pc so it runs without hardware requirement in CI
    async def mock_speak(text, voice):
        return True
    monkeypatch.setattr(VoiceEngine, "speak_on_pc", mock_speak)

    res = tool.execute(text="Goal finished successfully!")
    assert res["success"] is True
    assert "Goal finished successfully!" in res["output"]


# ==================== PHASE 2: PLAYWRIGHT VISION TESTS ====================

def test_vision_browser_tool_schema():
    tool = VisionBrowserTool()
    schema = tool.to_schema()
    assert schema["name"] == "vision_browser"
    actions = schema["parameters"]["properties"]["action"]["enum"]
    assert "navigate" in actions
    assert "screenshot" in actions
    assert "click" in actions
    assert "type" in actions
    assert "get_elements" in actions

def test_vision_browser_invalid_action():
    tool = VisionBrowserTool()
    res = tool.execute(action="non_existent_action")
    assert res["success"] is False


# ==================== PHASE 3: MCP INTEGRATION TESTS ====================

def test_mcp_manager_list_servers():
    mgr = MCPManager.get_instance()
    servers = mgr.list_servers()
    assert isinstance(servers, list)
    assert len(servers) >= 1

def test_mcp_manager_add_and_remove():
    mgr = MCPManager.get_instance()
    res = mgr.add_server(
        name="test_temp_mcp",
        command="python",
        args=["-m", "http.server"],
        description="Temporary test server"
    )
    assert res["success"] is True

    servers = [s["name"] for s in mgr.list_servers()]
    assert "test_temp_mcp" in servers

    rem_res = mgr.remove_server("test_temp_mcp")
    assert rem_res["success"] is True
    assert "test_temp_mcp" not in [s["name"] for s in mgr.list_servers()]

def test_mcp_tool_execution():
    tool = MCPTool()
    schema = tool.to_schema()
    assert schema["name"] == "manage_mcp"

    res = tool.execute(action="list_servers")
    assert res["success"] is True
    assert "Configured MCP Servers" in res["output"]


# ==================== PHASE 4: DESKTOP GUI TESTS ====================

def test_desktop_gui_screen_info():
    tool = DesktopGUIControlTool()
    res = tool.execute(action="get_screen_info")
    assert res["success"] is True
    assert "resolution" in res
    assert res["resolution"]["width"] > 0
    assert res["resolution"]["height"] > 0

def test_desktop_gui_send_keys(monkeypatch):
    import pyautogui
    tool = DesktopGUIControlTool()
    typed_content = []
    monkeypatch.setattr(pyautogui, "write", lambda text, interval: typed_content.append(text))

    res = tool.execute(action="send_keys", text="Hello from Helper-AI GUI")
    assert res["success"] is True
    assert "Hello from Helper-AI GUI" in res["output"]
    assert typed_content == ["Hello from Helper-AI GUI"]

def test_desktop_gui_press_key(monkeypatch):
    import pyautogui
    tool = DesktopGUIControlTool()
    pressed_keys = []
    monkeypatch.setattr(pyautogui, "press", lambda key: pressed_keys.append(key))

    res = tool.execute(action="press_key", key="enter")
    assert res["success"] is True
    assert "enter" in res["output"]
    assert pressed_keys == ["enter"]
