"""Tests for full PC and web automation capabilities."""
import pytest
from unittest.mock import MagicMock, patch
from core.tools.web_tools import FetchWebContentTool
from core.tools.browser_tools import BrowserAutomationTool
from core.tools.desktop_gui_tools import DesktopGUIControlTool, DesktopGUITool

def test_fetch_web_content_extraction(monkeypatch):
    tool = FetchWebContentTool()
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Helper-AI Test Page</title><script>console.log('ignore');</script></head>
    <body>
        <h1>Welcome to Helper-AI</h1>
        <p>This is a paragraph of meaningful text.</p>
        <h2>Features</h2>
        <ul><li>Automation</li><li>Desktop control</li></ul>
        <a href="https://example.com/about">About Us</a>
    </body>
    </html>
    """
    mock_resp = MagicMock()
    mock_resp.text = sample_html
    mock_resp.raise_for_status = MagicMock()

    monkeypatch.setattr("requests.get", lambda url, headers, timeout: mock_resp)

    res = tool.execute(url="https://example.com", max_characters=5000)
    assert res["success"] is True
    assert res["title"] == "Helper-AI Test Page"
    assert "Welcome to Helper-AI" in res["output"]
    assert "Features" in res["output"]
    assert "Automation" in res["output"]
    assert "About Us" in res["output"]

def test_browser_automation_new_actions_registered():
    tool = BrowserAutomationTool()
    actions = tool.parameters["properties"]["action"]["enum"]
    expected_actions = [
        "fetch_full_page",
        "scroll",
        "take_screenshot",
        "select_dropdown",
        "dismiss_popups",
        "execute_script"
    ]
    for act in expected_actions:
        assert act in actions

def test_browser_automation_scroll(monkeypatch):
    tool = BrowserAutomationTool()
    mock_browser = MagicMock()
    mock_browser.scroll.return_value = {"success": True, "direction": "down", "pixels": 500}
    monkeypatch.setattr("core.browser_driver.ProjectBrowser.get_instance", lambda: mock_browser)

    res = tool.execute(action="scroll", direction="down", pixels=500)
    assert res["success"] is True
    assert res["pixels"] == 500

def test_browser_automation_fetch_full_page(monkeypatch):
    tool = BrowserAutomationTool()
    mock_browser = MagicMock()
    mock_browser.get_full_page_content.return_value = {
        "success": True,
        "title": "Mock Title",
        "url": "https://mock.url",
        "total_characters": 32,
        "content": "Full body content of the webpage",
        "headings": ["Heading 1"],
        "buttons": ["Click Me"],
        "inputs": [],
        "links": []
    }
    monkeypatch.setattr("core.browser_driver.ProjectBrowser.get_instance", lambda: mock_browser)

    res = tool.execute(action="fetch_full_page")
    assert res["success"] is True
    assert "Full body content" in res["output"]

def test_desktop_gui_clipboard_actions(monkeypatch):
    tool = DesktopGUIControlTool()
    clipboard_storage = {}

    monkeypatch.setattr("pyperclip.copy", lambda text: clipboard_storage.update({"val": text}))
    monkeypatch.setattr("pyperclip.paste", lambda: clipboard_storage.get("val", ""))

    copy_res = tool.execute(action="clipboard_copy", text="Automated human clipboard text")
    assert copy_res["success"] is True
    assert clipboard_storage["val"] == "Automated human clipboard text"

    paste_res = tool.execute(action="clipboard_paste")
    assert paste_res["success"] is True
    assert paste_res["clipboard"] == "Automated human clipboard text"

def test_desktop_gui_hotkey(monkeypatch):
    tool = DesktopGUIControlTool()
    pressed_keys = []
    monkeypatch.setattr("pyautogui.hotkey", lambda *keys: pressed_keys.extend(keys))

    res = tool.execute(action="hotkey", keys="ctrl+shift+esc")
    assert res["success"] is True
    assert pressed_keys == ["ctrl", "shift", "esc"]

def test_desktop_gui_mouse_actions(monkeypatch):
    tool = DesktopGUIControlTool()
    actions_called = []
    monkeypatch.setattr("pyautogui.rightClick", lambda x, y: actions_called.append(("rightClick", x, y)))
    monkeypatch.setattr("pyautogui.doubleClick", lambda x, y: actions_called.append(("doubleClick", x, y)))
    monkeypatch.setattr("pyautogui.moveTo", lambda x, y, duration=0: actions_called.append(("moveTo", x, y)))
    monkeypatch.setattr("pyautogui.dragTo", lambda x, y, duration=0, button='primary': actions_called.append(("dragTo", x, y)))
    monkeypatch.setattr("pyautogui.scroll", lambda amount: actions_called.append(("scroll", amount)))

    res1 = tool.execute(action="right_click", x=100, y=200)
    assert res1["success"] is True
    assert ("rightClick", 100, 200) in actions_called

    res2 = tool.execute(action="double_click", x=150, y=250)
    assert res2["success"] is True
    assert ("doubleClick", 150, 250) in actions_called

    res3 = tool.execute(action="move_to", x=300, y=400)
    assert res3["success"] is True
    assert ("moveTo", 300, 400) in actions_called

    res4 = tool.execute(action="drag_to", x=500, y=600)
    assert res4["success"] is True
    assert ("dragTo", 500, 600) in actions_called

    res5 = tool.execute(action="scroll", amount=-300)
    assert res5["success"] is True
    assert ("scroll", -300) in actions_called

def test_desktop_gui_list_windows(monkeypatch):
    tool = DesktopGUIControlTool()
    mock_csv = '"Image Name","PID","Session Name","Session#","Mem Usage","Status","User Name","CPU Time","Window Title"\n"chrome.exe","1234","Console","1","50,000 K","Unknown","USER","0:01:00","LinkedIn - Google Chrome"\n"notepad.exe","5678","Console","1","10,000 K","Unknown","USER","0:00:01","Untitled - Notepad"\n'
    
    mock_subprocess = MagicMock()
    mock_subprocess.returncode = 0
    mock_subprocess.stdout = mock_csv
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_subprocess)

    res = tool.execute(action="list_windows")
    assert res["success"] is True
    assert len(res["windows"]) == 2
    assert any("LinkedIn" in w["title"] for w in res["windows"])
    assert any("Notepad" in w["title"] for w in res["windows"])

def test_browser_tab_management(monkeypatch):
    tool = BrowserAutomationTool()
    mock_browser = MagicMock()
    mock_browser.list_tabs.return_value = {
        "success": True,
        "tabs": [{"index": 0, "title": "Yahoo", "url": "https://login.yahoo.com/"}],
        "output": "Found 1 tab"
    }
    mock_browser.switch_tab.return_value = {
        "success": True,
        "output": "Switched to tab Yahoo"
    }
    mock_browser.close_tab.return_value = {
        "success": True,
        "output": "Closed tab"
    }
    monkeypatch.setattr("core.browser_driver.ProjectBrowser.get_instance", lambda: mock_browser)

    res_list = tool.execute(action="list_tabs")
    assert res_list["success"] is True
    assert len(res_list["tabs"]) == 1

    res_switch = tool.execute(action="switch_tab", target="Yahoo")
    assert res_switch["success"] is True

    res_close = tool.execute(action="close_tab")
    assert res_close["success"] is True

def test_llm_json_normalization_openai_format():
    from core.llm import LLMClient
    client = LLMClient(provider="groq", api_key="test_key")
    # Simulate OpenAI / Groq tool-use output
    groq_tool_output = '{"name": "search_web", "arguments": {"query": "Yahoo sign up with Google button", "max_results": 5}}'
    parsed = client._parse_json_response(groq_tool_output)
    assert parsed["action"] == "search_web"
    assert parsed["action_args"]["query"] == "Yahoo sign up with Google button"
    assert parsed["action_args"]["max_results"] == 5
    assert parsed["is_complete"] is False

def test_llm_groq_failed_generation_rescue(monkeypatch):
    from core.llm import LLMClient
    client = LLMClient(provider="groq", api_key="dummy_key")

    class MockGroqError(Exception):
        def __init__(self):
            self.body = {
                "error": {
                    "message": "Tool choice is none, but model called a tool",
                    "code": "tool_use_failed",
                    "failed_generation": '{"name": "search_web", "arguments": {"query": "Yahoo sign up with Google button", "max_results": 5}}'
                }
            }

    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create.side_effect = MockGroqError()
    monkeypatch.setattr("openai.OpenAI", lambda *args, **kwargs: mock_openai_client)

    result = client._call_groq("system prompt", "user prompt")
    assert result["action"] == "search_web"
    assert result["action_args"]["query"] == "Yahoo sign up with Google button"
