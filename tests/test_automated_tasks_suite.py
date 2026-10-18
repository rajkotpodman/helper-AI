"""Comprehensive Automated Verification Suite for Helper-AI.

Tests the Helper Agent across simple to advanced tasks for both PC and Internet:
- Simple PC: System Health, File Operations, Directory Listing.
- Intermediate PC: PowerShell/Python execution, Persistent Terminal sessions, Process Manager.
- Advanced PC: Self-Healing execution recovery, Windows UIA, App Memory Store.
- Simple Internet: Web fetch, Web search, Public API queries.
- Intermediate Internet: Batch web fetch, File download, Deep web crawling.
- Advanced Internet: Browser Set-of-Marks tagging, Deep research synthesis.
- End-to-End Agent Goals: Full autonomous agent run loops on PC and Internet.
"""

import os
import sys
import time
import json
import asyncio
import pytest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.tools import ToolRegistry
from core.agent import HelperAgent
from core.llm import LLMClient
from core.reverse_engineering.app_memory_store import AppMemoryStore
from core.command_engine.persistent_shell import PersistentShellSession


@pytest.fixture(scope="module")
def tools():
    return ToolRegistry()


@pytest.fixture(scope="module")
def scratch_dir():
    d = PROJECT_ROOT / "scratch" / "auto_test_sandbox"
    d.mkdir(parents=True, exist_ok=True)
    yield d


# =====================================================================
# TIER 1: SIMPLE PC TASKS
# =====================================================================

def test_simple_pc_system_health(tools):
    """Test 1.1: System Health diagnostic queries CPU, RAM, Disk, OS."""
    tool = tools.get_tool("get_system_health")
    assert tool is not None
    res = tool.execute()
    assert res.get("success") is True, f"System health failed: {res}"
    assert "cpu_percent" in res or "cpu" in str(res).lower()
    assert "ram_percent" in res or "ram" in str(res).lower()
    assert "disk_percent" in res or "disk" in str(res).lower()


def test_simple_pc_file_crud_and_directory_listing(tools, scratch_dir):
    """Test 1.2: File write, read, and directory listing."""
    write_tool = tools.get_tool("write_file")
    read_tool = tools.get_tool("read_file")
    list_tool = tools.get_tool("list_directory")

    test_file = scratch_dir / "test_notes.txt"
    test_content = "Helper-AI Autonomous Agent: Simple PC File Test Complete.\nLine 2: 100% verified."

    # 1. Write file
    w_res = write_tool.execute(path=str(test_file), content=test_content)
    assert w_res.get("success") is True, f"Write file failed: {w_res}"
    assert test_file.exists()

    # 2. Read file back
    r_res = read_tool.execute(path=str(test_file))
    assert r_res.get("success") is True, f"Read file failed: {r_res}"
    assert test_content in r_res.get("content", "")

    # 3. List directory
    l_res = list_tool.execute(path=str(scratch_dir))
    assert l_res.get("success") is True, f"List directory failed: {l_res}"
    entries = str(l_res.get("entries", "") or l_res.get("output", ""))
    assert "test_notes.txt" in entries


def test_simple_pc_search_files(tools, scratch_dir):
    """Test 1.3: Search files by pattern."""
    search_tool = tools.get_tool("search_files")
    res = search_tool.execute(directory=str(scratch_dir), pattern="*.txt")
    assert res.get("success") is True, f"Search files failed: {res}"
    matches = res.get("matches", [])
    assert any("test_notes.txt" in str(m) for m in matches)


# =====================================================================
# TIER 2: INTERMEDIATE PC TASKS
# =====================================================================

def test_intermediate_pc_execute_powershell(tools):
    """Test 2.1: PowerShell execution with mathematical / environmental output."""
    tool = tools.get_tool("execute_powershell")
    res = tool.execute(command="Write-Output (40 + 2)")
    assert res.get("success") is True, f"PowerShell failed: {res}"
    output = res.get("output", "").strip()
    assert "42" in output


def test_intermediate_pc_execute_python(tools):
    """Test 2.2: Python execution inside helper sandbox."""
    tool = tools.get_tool("execute_python_code")
    assert tool is not None
    code = "import math; print(f'PI_ROUNDED={round(math.pi, 4)}')"
    res = tool.execute(code=code)
    assert res.get("success") is True, f"Python tool failed: {res}"
    output = res.get("output", "").strip()
    assert "PI_ROUNDED=3.1416" in output


def test_intermediate_pc_persistent_shell_state(tools, scratch_dir):
    """Test 2.3: Persistent stateful shell maintains variables & working directory."""
    term_tool = tools.get_tool("universal_terminal")
    session_id = f"test_auto_{int(time.time())}"

    # Step A: Change directory and define a variable
    cmd1 = f"Set-Variable -Name AGENT_KEY -Value 'HELPER_VERIFIED_999'; Write-Output 'STEP1_OK'"
    res1 = term_tool.execute(action="execute", command=cmd1, session_id=session_id)
    assert res1.get("success") is True, f"Persistent shell step 1 failed: {res1}"

    # Step B: Read variable back in the same persistent session
    cmd2 = "Write-Output \"VAL=$($AGENT_KEY)\""
    res2 = term_tool.execute(action="execute", command=cmd2, session_id=session_id)
    assert res2.get("success") is True, f"Persistent shell step 2 failed: {res2}"
    assert "HELPER_VERIFIED_999" in res2.get("output", "")


def test_intermediate_pc_process_manager(tools):
    """Test 2.4: Process Manager lists running processes."""
    tool = tools.get_tool("manage_processes")
    assert tool is not None
    res = tool.execute(action="list")
    assert res.get("success") is True, f"Process manager failed: {res}"
    processes = str(res.get("processes", "") or res.get("output", ""))
    assert "pid" in processes.lower() or "python" in processes.lower()


# =====================================================================
# TIER 3: ADVANCED PC TASKS & SELF-HEALING
# =====================================================================

def test_advanced_pc_self_healing_recovery(tools):
    """Test 3.1: Self-healing command intercept when an invalid/hallucinated command is passed."""
    ps_tool = tools.get_tool("execute_powershell")
    # Simulate a hallucinated PowerShell module command for Ollama
    res = ps_tool.execute(command="Get-InstalledModule -Name ollama")
    assert res.get("success") is True or "hint" in str(res).lower()
    out = str(res.get("output", "")).lower()
    # Interceptor should catch this and either provide self-healing output or recovery hint
    assert "self-healing" in out or "retrieved installed ollama models" in out or "ollama" in out


def test_advanced_pc_windows_uia_discovery(tools):
    """Test 3.2: Windows UI Automation discovers active windows and control trees."""
    tool = tools.get_tool("windows_uia")
    assert tool is not None
    res = tool.execute(action="list_windows")
    assert res.get("success") is True, f"Windows UIA list_windows failed: {res}"
    assert "windows" in res
    assert "window_count" in res
    assert isinstance(res.get("windows"), list)


def test_advanced_pc_rea_app_memory(tools):
    """Test 3.3: Reverse Engineering App Memory Store saving and retrieval."""
    store = AppMemoryStore.get_instance()
    # Save a test profile
    store.save_app_profile({
        "app_name": "Mock Calculator",
        "app_slug": "mock_calc",
        "process_name": "calc.exe",
        "verified_hotkeys": {
            "clear": "Esc",
            "calculate": "Enter"
        },
        "controls": {"equals": "btn_equals", "clear": "btn_clear"}
    })

    # Retrieve profile
    prof = store.get_app_profile("mock_calc")
    assert prof is not None
    assert prof.get("app_name") == "Mock Calculator"
    assert prof.get("verified_hotkeys", {}).get("clear") == "Esc"


# =====================================================================
# TIER 4: SIMPLE INTERNET TASKS
# =====================================================================

def test_simple_internet_fetch_web_content(tools):
    """Test 4.1: Fetch live web content via HTTP request."""
    tool = tools.get_tool("fetch_web_content")
    # Test with a highly reliable endpoint
    res = tool.execute(url="https://httpbin.org/get")
    assert res.get("success") is True, f"Fetch web content failed: {res}"
    content = str(res.get("content", ""))
    assert "headers" in content or "origin" in content or "args" in content


def test_simple_internet_search_web(tools):
    """Test 4.2: Web search queries DuckDuckGo / web search engine."""
    tool = tools.get_tool("search_web")
    res = tool.execute(query="Python programming language official website")
    assert res.get("success") is True, f"Web search failed: {res}"
    results = res.get("results", []) or str(res.get("output", ""))
    assert len(str(results)) > 20


# =====================================================================
# TIER 5: INTERMEDIATE & ADVANCED INTERNET TASKS
# =====================================================================

def test_intermediate_internet_batch_fetch(tools):
    """Test 5.1: Batch web fetch fetches multiple URLs concurrently."""
    tool = tools.get_tool("batch_fetch_web")
    assert tool is not None
    urls = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/get"
    ]
    res = tool.execute(urls=urls)
    assert res.get("success") is True, f"Batch fetch failed: {res}"
    results = res.get("results", {})
    assert len(results) >= 1


def test_intermediate_internet_file_download(tools, scratch_dir):
    """Test 5.2: Download a file from the internet and verify on disk."""
    tool = tools.get_tool("download_file")
    target_path = scratch_dir / "downloaded_sample.txt"
    # Use a small reliable test endpoint
    res = tool.execute(url="https://httpbin.org/robots.txt", destination_path=str(target_path))
    assert res.get("success") is True, f"Download file failed: {res}"
    assert target_path.exists()
    assert target_path.stat().st_size > 0


def test_advanced_internet_browser_set_of_marks(tools):
    """Test 5.3: Web Set-of-Marks visual tagging schema and validation."""
    tool = tools.get_tool("browser_automation")
    # Verify browser_automation supports SoM actions
    supported = tool.get_schema()
    actions_desc = str(supported)
    assert "tag_elements" in actions_desc or "tag" in actions_desc
    assert "click_mark" in actions_desc
    assert "type_mark" in actions_desc


# =====================================================================
# TIER 6: END-TO-END AUTONOMOUS AGENT EXECUTION
# =====================================================================

@pytest.mark.asyncio
async def test_end_to_end_agent_pc_goal(scratch_dir):
    """Test 6.1: Full autonomous agent run loop for a PC goal."""
    report_file = scratch_dir / "agent_diag_summary.txt"
    goal = f"Check system health and write the output to '{report_file}'"

    # Use RuleEngine or active provider to test deterministic goal execution
    agent = HelperAgent(max_steps=5)
    result = await agent.run(goal)
    assert result.get("success") is True, f"Agent PC goal failed: {result}"
    # Verify that the agent actually executed steps
    assert len(agent.memory_recorder.file_path.read_text(encoding="utf-8")) > 0


@pytest.mark.asyncio
async def test_end_to_end_agent_internet_goal(scratch_dir):
    """Test 6.2: Full autonomous agent run loop for an Internet research & report goal."""
    report_file = scratch_dir / "internet_research_summary.txt"
    goal = f"Fetch web content from https://httpbin.org/get and write summary to '{report_file}'"

    agent = HelperAgent(max_steps=5)
    result = await agent.run(goal)
    assert result.get("success") is True, f"Agent Internet goal failed: {result}"
    assert len(agent.memory_recorder.file_path.read_text(encoding="utf-8")) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
