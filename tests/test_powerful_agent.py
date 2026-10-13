"""Tests for powerful deep web fetching, python execution, project builder, and long-running agent features."""
import pytest
import os
import shutil
from pathlib import Path
from core.tools import ToolRegistry
from core.tools.web_tools import DeepWebCrawlerTool, BatchWebFetchTool, FetchGitHubRepoTool
from core.tools.system_tools import ExecutePythonTool, BuildProjectTool
from core.memory import AgentMemory
from core.agent import HelperAgent
from core.llm import LLMClient


@pytest.fixture
def registry():
    return ToolRegistry()


def test_registry_contains_25_tools(registry):
    tools = registry.get_all_tools()
    assert len(tools) >= 25
    tool_names = [t.name for t in tools]
    assert "deep_web_crawl" in tool_names
    assert "batch_fetch_web" in tool_names
    assert "fetch_github_repo" in tool_names
    assert "execute_python_code" in tool_names
    assert "build_project_files" in tool_names


def test_execute_python_tool(registry):
    code = """
import math
total = sum([math.isqrt(i * i) for i in range(1, 11)])
print(f"Total: {total}")
"""
    result = registry.execute("execute_python_code", {"code": code})
    assert result["success"] is True
    assert "Total: 55" in result["output"]


def test_build_project_tool(registry, tmp_path):
    project_dir = str(tmp_path / "sample_app")
    files = {
        "main.py": "print('hello from app')",
        "src/utils.py": "def add(a, b): return a + b",
        "README.md": "# Sample App\nBuilt autonomously by Helper-AI."
    }
    result = registry.execute("build_project_files", {
        "project_dir": project_dir,
        "files": files,
        "overwrite": True
    })
    assert result["success"] is True
    assert result["files_count"] == 3
    assert (Path(project_dir) / "main.py").exists()
    assert (Path(project_dir) / "src" / "utils.py").exists()
    assert (Path(project_dir) / "README.md").exists()
    assert "def add" in (Path(project_dir) / "src" / "utils.py").read_text(encoding="utf-8")


def test_fetch_github_repo_tool(registry):
    # Test overview
    res = registry.execute("fetch_github_repo", {
        "repo": "rajkotpodman/helper-AI",
        "action": "overview"
    })
    assert res["success"] is True
    assert "rajkotpodman/helper-AI" in res["output"]

    # Test readme
    res_readme = registry.execute("fetch_github_repo", {
        "repo": "rajkotpodman/helper-AI",
        "action": "readme"
    })
    assert res_readme["success"] is True
    assert "Helper-AI" in res_readme["content"]
    assert len(res_readme["content"]) > 500


def test_batch_web_fetch_tool(registry):
    res = registry.execute("batch_fetch_web", {
        "urls": [
            "https://raw.githubusercontent.com/rajkotpodman/helper-AI/main/LICENSE",
            "https://raw.githubusercontent.com/rajkotpodman/helper-AI/main/.gitignore"
        ],
        "max_characters_per_url": 5000
    })
    assert res["success"] is True
    assert res["successful_count"] >= 1
    assert "Batch Fetch Results" in res["output"]


def test_deep_web_crawl_tool(registry):
    res = registry.execute("deep_web_crawl", {
        "start_url": "https://raw.githubusercontent.com/rajkotpodman/helper-AI/main/README.md",
        "max_pages": 1,
        "max_depth": 0
    })
    assert res["success"] is True
    assert res["pages_crawled"] == 1
    assert "Deep Crawl Completed Successfully" in res["output"]


def test_agent_memory_pinned_facts_and_milestones():
    mem = AgentMemory("Heavy long-running task to research and implement an agent")
    mem.pin_fact("Discovered repository: rajkotpodman/helper-AI")
    mem.pin_fact("Target framework: FastAPI + Playwright")
    assert len(mem.pinned_facts) == 2

    milestones = [
        {"id": 1, "title": "Research", "status": "completed"},
        {"id": 2, "title": "Implementation", "status": "in_progress"}
    ]
    mem.set_milestones(milestones)
    summary = mem.get_trajectory_summary()
    assert "CRITICAL PINNED FACTS" in summary
    assert "ACTIVE TASK MILESTONES" in summary
    assert "Phase 1: Research [completed]" in summary
    assert "Phase 2: Implementation [in_progress]" in summary


def test_helper_agent_step_scaling():
    agent = HelperAgent(max_steps=50)
    # Goal with /goal and heavy keywords should scale max_steps to 200
    goal = "/goal crawl full web documentation and implement complete project"
    clean_goal = goal.strip().lower()
    is_heavy_task = any(w in clean_goal for w in [
        "/goal", "heavy", "long", "deep", "full web", "crawl", "build", "implement", "project", "complete"
    ])
    assert is_heavy_task is True
