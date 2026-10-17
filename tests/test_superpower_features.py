"""Unit and Integration Tests for Superpower Features:
1. Phase 1: Persistent Stateful Shell Sessions (Open Interpreter Pattern)
2. Phase 2: Windows UI Automation (UIA) Tool (Microsoft UFO Pattern)
3. Phase 3: Web Set-of-Marks Tagging (Browser-Use Pattern)
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

from core.command_engine.persistent_shell import PersistentShellSession, PersistentShellManager
from core.tools.universal_terminal_tools import UniversalTerminalTool
from core.tools.windows_uia_tools import WindowsUIATool
from core.tools.browser_tools import BrowserAutomationTool
from core.browser_driver import ProjectBrowser


# =============================================================================
# Phase 1: Persistent Shell Sessions Tests
# =============================================================================

def test_persistent_shell_variable_persistence():
    """Tests that variables defined in step 1 remain available in step 2."""
    sess = PersistentShellManager.get_session("test_pytest_session")
    try:
        # Step 1: Assign variable
        res1 = sess.execute('$pytest_var = "SUPERPOWER_OK"; Write-Output "STEP1_DONE"')
        assert res1["success"] is True
        assert "STEP1_DONE" in res1["output"]

        # Step 2: Read variable
        res2 = sess.execute('Write-Output "VAL:$pytest_var"')
        assert res2["success"] is True
        assert "VAL:SUPERPOWER_OK" in res2["output"]
    finally:
        sess.close()


def test_persistent_shell_directory_persistence():
    """Tests that directory changes persist across commands."""
    sess = PersistentShellManager.get_session("test_pytest_dir_session")
    try:
        # Step 1: Navigate into 'core'
        res1 = sess.execute('cd core; Write-Output "IN_CORE"')
        assert res1["success"] is True
        assert "core" in res1["cwd"].lower()

        # Step 2: Query location without re-navigating
        res2 = sess.execute('(Get-Location).Path')
        assert res2["success"] is True
        assert "core" in res2["output"].lower()
    finally:
        sess.close()


def test_universal_terminal_tool_persistent_actions():
    """Tests UniversalTerminalTool integration with persistent shell."""
    tool = UniversalTerminalTool()

    # Session Info
    info = tool.execute(action="session_info", session_id="test_tool_session")
    assert "session_id" in info
    assert info["is_alive"] is True

    # Multi-step execution via tool
    r1 = tool.execute(command='$tool_var = 12345; Write-Output "SAVED"', session_id="test_tool_session")
    assert r1["success"] is True
    assert "SAVED" in r1["output"]

    r2 = tool.execute(command='Write-Output "READ:$tool_var"', session_id="test_tool_session")
    assert r2["success"] is True
    assert "READ:12345" in r2["output"]

    # Reset session
    reset_res = tool.execute(action="reset_session", session_id="test_tool_session")
    assert reset_res["success"] is True

    # Cleanup
    sess = PersistentShellManager.get_session("test_tool_session")
    sess.close()


# =============================================================================
# Phase 2: Windows UI Automation (UIA) Tests
# =============================================================================

def test_windows_uia_tool_initialization():
    """Tests tool metadata and parameter schema."""
    tool = WindowsUIATool()
    assert tool.name == "windows_uia"
    assert "list_windows" in tool.parameters["properties"]["action"]["enum"]
    assert "click_control" in tool.parameters["properties"]["action"]["enum"]
    assert "type_control" in tool.parameters["properties"]["action"]["enum"]
    assert "select_menu" in tool.parameters["properties"]["action"]["enum"]


def test_windows_uia_tool_list_windows():
    """Tests list_windows execution."""
    tool = WindowsUIATool()
    res = tool.execute(action="list_windows")
    assert res["success"] is True
    assert "windows" in res
    assert isinstance(res["windows"], list)


def test_windows_uia_tool_missing_parameters():
    """Tests that missing required parameters return clean errors."""
    tool = WindowsUIATool()

    # click_control without control_name
    r1 = tool.execute(action="click_control")
    assert r1["success"] is False
    assert "control_name is required" in r1["error"]

    # type_control without control_name
    r2 = tool.execute(action="type_control")
    assert r2["success"] is False
    assert "control_name is required" in r2["error"]

    # type_control without text
    r3 = tool.execute(action="type_control", control_name="Username")
    assert r3["success"] is False
    assert "text is required" in r3["error"]

    # select_menu without menu_path
    r4 = tool.execute(action="select_menu")
    assert r4["success"] is False
    assert "menu_path is required" in r4["error"]


# =============================================================================
# Phase 3: Web Set-of-Marks Tagging Tests
# =============================================================================

def test_browser_automation_tool_set_of_marks_schema():
    """Tests that BrowserAutomationTool exposes Set-of-Marks actions."""
    tool = BrowserAutomationTool()
    actions = tool.parameters["properties"]["action"]["enum"]
    assert "tag_elements" in actions
    assert "set_of_marks" in actions
    assert "click_mark" in actions
    assert "type_mark" in actions
    assert "clear_marks" in actions
    assert "mark_id" in tool.parameters["properties"]


def test_browser_driver_set_of_marks_mocked():
    """Tests Set-of-Marks execution logic using mocked Selenium driver."""
    browser = ProjectBrowser.get_instance()
    mock_driver = MagicMock()

    # Mock execute_script return values
    mock_driver.execute_script.side_effect = [
        # inject_set_of_marks
        [{"mark_id": 1, "tag": "button", "text": "Submit", "type": "submit"}],
        # click_mark
        {"success": True, "tag": "button", "text": "Submit"},
        # type_mark
        {"success": True, "tag": "input", "current_value": "hello@world.com"},
        # clear_marks
        {"success": True, "output": "Cleared all marks."}
    ]

    with patch.object(browser, "get_driver", return_value=mock_driver):
        # 1. Inject marks
        tag_res = browser.inject_set_of_marks()
        assert tag_res["success"] is True
        assert tag_res["total_marked"] == 1
        assert tag_res["marks"][0]["mark_id"] == 1

        # 2. Click mark
        click_res = browser.click_mark(1)
        assert click_res["success"] is True
        assert click_res["tag"] == "button"

        # 3. Type into mark
        type_res = browser.type_mark(1, "hello@world.com")
        assert type_res["success"] is True
        assert type_res["current_value"] == "hello@world.com"

        # 4. Clear marks
        clear_res = browser.clear_marks()
        assert clear_res["success"] is True


def test_browser_tool_mark_validation():
    """Tests BrowserAutomationTool validation when mark_id is omitted."""
    tool = BrowserAutomationTool()

    # click_mark without mark_id
    r1 = tool.execute(action="click_mark")
    assert r1["success"] is False
    assert "Please provide 'mark_id'" in r1["output"]

    # type_mark without mark_id
    r2 = tool.execute(action="type_mark", text="sample")
    assert r2["success"] is False
    assert "Please provide 'mark_id'" in r2["output"]
