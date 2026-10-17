"""Integration and Unit Tests for REA Reverse Engineering & App Memory Suite."""

import pytest
import tempfile
import os
from pathlib import Path

from core.reverse_engineering.rea_bridge import REABridge
from core.reverse_engineering.app_memory_store import AppMemoryStore
from core.reverse_engineering.app_analyzer import ReverseEngineeringEngine
from core.reverse_engineering.fast_operator import FastAppOperator
from core.tools import ToolRegistry


def test_rea_bridge_availability():
    """Verifies that the compiled REA CLI is detected, operational, and returns version 6.5.0."""
    bridge = REABridge.get_instance()
    assert bridge.is_available() is True, "REA should be compiled and available"
    version = bridge.get_version()
    assert "6.5.0" in version, f"Expected 6.5.0 in version, got {version}"


def test_rea_mcp_tools_discovery():
    """Verifies that REA exposes over 200 MCP reverse engineering tools via stdio."""
    bridge = REABridge.get_instance()
    tools = bridge.list_mcp_tools()
    assert isinstance(tools, list)
    assert len(tools) >= 200, f"Expected >= 200 REA tools, got {len(tools)}"
    tool_names = [t["name"] for t in tools]
    assert "analyze_javascript_application" in tool_names or "inspect_artifact" in tool_names


def test_app_memory_store_lifecycle():
    """Tests saving, retrieving, and searching app profiles in AppMemoryStore."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = AppMemoryStore(memory_dir=Path(temp_dir))
        
        # Test default seeds
        all_profs = store.list_all_profiles()
        assert len(all_profs) >= 5, "Default foundational apps should be seeded"
        
        # Test querying Notepad
        np = store.get_app_profile("notepad")
        assert np is not None
        assert np["app_slug"] == "notepad"
        assert "save" in np["fast_path"]["keyboard_shortcuts"]
        
        # Test goal matching
        matched = store.find_matching_profile_for_goal("Please open notepad and write my notes")
        assert matched is not None
        assert matched["app_slug"] == "notepad"
        
        # Test AI prompt formatting
        ai_prompt = store.format_for_ai_prompt(np)
        assert "KNOWN APP MEMORY AVAILABLE" in ai_prompt
        assert "ctrl+s" in ai_prompt
        
        # Test saving custom reverse engineered app
        custom_app = {
            "app_name": "TestIDE",
            "app_slug": "test_ide",
            "process_name": "test_ide.exe",
            "app_type": "electron",
            "fast_path": {
                "launch_command": "test_ide",
                "keyboard_shortcuts": {
                    "build": "ctrl+b",
                    "run": "f5"
                },
                "ui_controls": [
                    {"name": "RunButton", "type": "Button", "automation_id": "btnRun"}
                ]
            }
        }
        save_res = store.save_app_profile(custom_app, sync_markdown=False)
        assert save_res["success"] is True
        
        # Verify retrieved
        retrieved = store.get_app_profile("test_ide")
        assert retrieved is not None
        assert retrieved["fast_path"]["keyboard_shortcuts"]["build"] == "ctrl+b"


def test_reverse_engineering_engine_web_target():
    """Tests reverse-engineering a web application target and registering profile."""
    engine = ReverseEngineeringEngine.get_instance()
    res = engine.reverse_engineer(target="https://example.com", depth="quick", save_to_memory=True)
    assert res["success"] is True
    assert "app_profile" in res
    assert res["app_profile"]["app_type"] == "web_application"
    
    # Check that AppMemoryStore now has it
    store = AppMemoryStore.get_instance()
    prof = store.get_app_profile("example_com")
    assert prof is not None


def test_reverse_engineering_tools_registration():
    """Verifies that all reverse-engineering tools are registered in ToolRegistry."""
    registry = ToolRegistry()
    
    tool_re = registry.get_tool("reverse_engineer_app")
    tool_query = registry.get_tool("query_app_memory")
    tool_fast = registry.get_tool("fast_app_operate")
    tool_mcp = registry.get_tool("mcp_rea_call")
    
    assert tool_re is not None
    assert tool_query is not None
    assert tool_fast is not None
    assert tool_mcp is not None
    
    # Test query_app_memory execute
    res_list = tool_query.execute(action="list")
    assert res_list["success"] is True
    assert len(res_list["profiles"]) >= 5
    
    res_get = tool_query.execute(action="get", app_name="notepad")
    assert res_get["success"] is True
    assert "Notepad" in res_get["output"]
