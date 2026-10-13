"""Comprehensive Test Suite for Universal Terminal & Cross-Platform Command Engine.

Tests:
- OS & Environment Detection (OSDetector)
- Encyclopedic Cross-Platform Command Synthesis (CommandEncyclopedia)
- Community Command Cheat Sheet Fetcher (CommandFetcher)
- Universal Command Execution & Background Daemon Tracking (UniversalCommandExecutor)
- Tool Registry Integration (UniversalTerminalTool, SynthesizeOSCommandTool, CommandHubTool)
- Rule Engine Autonomous Routing
"""

import os
import sys
import pytest
from core.command_engine.os_detector import OSDetector
from core.command_engine.command_encyclopedia import CommandEncyclopedia
from core.command_engine.command_fetcher import CommandFetcher
from core.command_engine.executor import UniversalCommandExecutor
from core.tools import ToolRegistry
from core.llm import LLMClient


# ============================================================================
# 1. OS & Environment Detection Tests
# ============================================================================

def test_os_detector_detect_os():
    os_info = OSDetector.detect_os()
    assert "family" in os_info
    assert os_info["family"] in ["windows", "linux", "macos", "wsl", "bsd", "unknown"]
    assert "architecture" in os_info
    assert "distro" in os_info


def test_os_detector_available_shells():
    shells = OSDetector.detect_available_shells()
    assert isinstance(shells, dict)
    # On Windows or Linux, at least one standard shell should be found
    assert len(shells) >= 1


def test_os_detector_preferred_shell():
    pref = OSDetector.get_preferred_shell()
    assert "shell" in pref
    assert "binary" in pref
    assert "type" in pref


def test_os_detector_system_context():
    ctx = OSDetector.get_system_context()
    assert "os" in ctx
    assert "preferred_shell" in ctx
    assert "package_managers" in ctx
    assert "is_elevated" in ctx


# ============================================================================
# 2. Command Encyclopedia & Synthesis Tests
# ============================================================================

def test_command_encyclopedia_catalog():
    catalog = CommandEncyclopedia.get_catalog()
    assert len(catalog) >= 10
    assert "kill_process_by_port" in catalog
    assert "find_large_files" in catalog
    assert "disk_usage" in catalog


def test_command_encyclopedia_recipe_substitution():
    recipe = CommandEncyclopedia.get_recipe(
        "kill_process_by_port",
        os_family="windows",
        params={"port": 9050}
    )
    assert recipe is not None
    assert "9050" in recipe["command"]
    assert recipe["shell_type"] == "powershell"

    recipe_posix = CommandEncyclopedia.get_recipe(
        "kill_process_by_port",
        os_family="linux",
        params={"port": 9050}
    )
    assert recipe_posix is not None
    assert "9050" in recipe_posix["command"]
    assert recipe_posix["shell_type"] == "bash"


def test_command_encyclopedia_search():
    matches = CommandEncyclopedia.search_recipes("port")
    assert len(matches) >= 1
    names = [m["name"] for m in matches]
    assert any("port" in n for n in names)


def test_command_encyclopedia_synthesize_for_intent():
    res = CommandEncyclopedia.synthesize_for_intent("kill process occupying port 8080", os_family="windows")
    assert res is not None
    assert "8080" in res["command"]

    res_disk = CommandEncyclopedia.synthesize_for_intent("check free disk space on drive", os_family="windows")
    assert res_disk is not None
    assert "Get-PSDrive" in res_disk["command"]


# ============================================================================
# 3. Command Fetcher Tests
# ============================================================================

def test_command_fetcher_local_or_encyclopedia():
    # Test built-in encyclopedia fallback for a known tool
    res = CommandFetcher.fetch_command_cheatsheet("port")
    assert res["success"] is True
    assert "content" in res


# ============================================================================
# 4. Universal Command Executor Tests
# ============================================================================

def test_universal_executor_sync():
    # Test a simple cross-platform python print
    res = UniversalCommandExecutor.execute_sync("python -c \"print('HELPER_AI_OK')\"")
    assert res["success"] is True
    assert res["exit_code"] == 0
    assert "HELPER_AI_OK" in res["output"]


def test_universal_executor_background_lifecycle():
    # Launch a quick non-blocking task
    bg_res = UniversalCommandExecutor.execute_background(
        "python -c \"import time; time.sleep(0.5); print('BG_TASK_DONE')\"",
        task_name="test_bg"
    )
    assert bg_res["success"] is True
    task_id = bg_res["task_id"]

    # Check status while running
    status_res = UniversalCommandExecutor.get_task_status(task_id)
    assert status_res["success"] is True
    assert status_res["task_id"] == task_id

    # Wait for completion
    import time
    time.sleep(1.2)
    done_status = UniversalCommandExecutor.get_task_status(task_id)
    assert done_status["status"] == "completed"
    assert "BG_TASK_DONE" in done_status["recent_output"]


# ============================================================================
# 5. Tool Registry Integration Tests
# ============================================================================

def test_tool_registry_has_universal_terminal_tools():
    registry = ToolRegistry()
    tools = registry.get_all_tools()
    tool_names = [t.name for t in tools]
    assert "universal_terminal" in tool_names
    assert "synthesize_os_command" in tool_names
    assert "command_hub" in tool_names


def test_universal_terminal_tool_execution():
    registry = ToolRegistry()
    tool = registry.get_tool("universal_terminal")
    res = tool.execute(command="python -c \"print('TERMINAL_TOOL_TEST')\"")
    assert res["success"] is True
    assert "TERMINAL_TOOL_TEST" in res["output"]


def test_synthesize_os_command_tool_execution():
    registry = ToolRegistry()
    tool = registry.get_tool("synthesize_os_command")
    res = tool.execute(intent="kill process on port 3000", target_os="windows", execute_now=False)
    assert res["success"] is True
    assert "3000" in res["synthesized_command"]


def test_command_hub_tool_list_recipes():
    registry = ToolRegistry()
    tool = registry.get_tool("command_hub")
    res = tool.execute(action="list_all_recipes")
    assert res["success"] is True
    assert res["total_recipes"] >= 10


# ============================================================================
# 6. LLM Rule Engine Routing Tests
# ============================================================================

def test_rule_engine_routing_for_command_hub():
    llm = LLMClient(provider="rule_engine")
    step = llm.generate_step(
        goal="download cheatsheet for ffmpeg terminal commands",
        trajectory_summary="No previous steps executed yet.",
        tool_schemas="",
        os_info={"os": "Windows", "release": "11"}
    )
    assert step["action"] == "command_hub"
    assert step["action_args"]["topic"] == "ffmpeg"
    assert step["is_complete"] is True


def test_rule_engine_routing_for_synthesize_command():
    llm = LLMClient(provider="rule_engine")
    step = llm.generate_step(
        goal="synthesize command to check your os and ready for that os all command",
        trajectory_summary="No previous steps executed yet.",
        tool_schemas="",
        os_info={"os": "Windows", "release": "11"}
    )
    assert step["action"] == "synthesize_os_command"
    assert step["is_complete"] is True
