"""Comprehensive Test Suite for Helper-AI Superpowers.

Tests:
- Superpower Workflow Orchestrator (SuperpowerOrchestrator)
- Superpower Deep Research Engine (SuperpowerResearchEngine)
- Superpower Code Studio (SuperpowerCodeStudio)
- Superpower System Optimizer & Diagnostics (SuperpowerSystemOptimizer)
- 32-Tool Registry Integration & Schema Checks
- LLM Rule Engine Superpower Routing
"""

import sys
import pytest
from pathlib import Path

from core.superpowers.orchestrator import SuperpowerOrchestrator
from core.superpowers.research_engine import SuperpowerResearchEngine
from core.superpowers.code_studio import SuperpowerCodeStudio
from core.superpowers.system_optimizer import SuperpowerSystemOptimizer
from core.tools import ToolRegistry
from core.llm import LLMClient


# ============================================================================
# 1. Orchestrator Tests
# ============================================================================

def test_orchestrator_planning():
    orchestrator = SuperpowerOrchestrator()
    plan = orchestrator.plan_workflow("Build an enterprise multi-agent system")
    assert plan["status"] == "planned"
    assert plan["total_phases"] == 5
    assert len(plan["milestones"]) == 5
    assert plan["milestones"][0]["id"] == "discovery"


def test_orchestrator_phase_advancement():
    orchestrator = SuperpowerOrchestrator()
    plan = orchestrator.plan_workflow("Automate report generation")
    pid = plan["pipeline_id"]

    res = orchestrator.advance_phase(pid, 0, "Discovered requirements", success=True)
    assert res["success"] is True
    assert res["milestones"][0]["status"] == "completed"

    report = orchestrator.generate_pipeline_report(pid)
    assert "AUTONOMOUS PIPELINE EXECUTION REPORT" in report
    assert "Phase 1:" in report


# ============================================================================
# 2. Research Engine Tests
# ============================================================================

def test_research_engine_subqueries():
    engine = SuperpowerResearchEngine()
    queries = engine.generate_subqueries("Autonomous Agents", count=4)
    assert len(queries) == 4
    assert any("overview" in q for q in queries)
    assert any("benchmarks" in q for q in queries)


def test_research_engine_dossier_formatting():
    engine = SuperpowerResearchEngine()
    sample_sources = [
        {"title": "Agentic Architecture", "url": "https://example.com/agents", "text": "Agents autonomously plan and execute."}
    ]
    dossier = engine._build_dossier_markdown("AI Agents", sample_sources, 1.25)
    assert "Executive Intelligence Dossier" in dossier
    assert "Agentic Architecture" in dossier
    assert "https://example.com/agents" in dossier


# ============================================================================
# 3. Code Studio Tests
# ============================================================================

def test_code_studio_project_creation_and_execution(tmp_path):
    project_dir = tmp_path / "super_project"
    files = {
        "calculator.py": "def add(a, b):\n    return a + b\n",
        "main.py": "from calculator import add\nprint(f'SUM={add(5, 7)}')\n"
    }

    res = SuperpowerCodeStudio.create_project(
        project_dir=str(project_dir),
        files=files,
        run_entrypoint="main.py"
    )

    assert res["success"] is True
    assert res["total_files_created"] == 2
    assert res["syntax_valid"] is True
    assert res["execution_verification"] is not None
    assert "SUM=12" in res["execution_verification"]["stdout"]


def test_code_studio_syntax_error_detection(tmp_path):
    project_dir = tmp_path / "invalid_project"
    files = {
        "broken.py": "def broken_syntax(:\n    pass\n"
    }

    res = SuperpowerCodeStudio.create_project(
        project_dir=str(project_dir),
        files=files
    )

    assert res["success"] is False
    assert res["syntax_valid"] is False
    assert len(res["syntax_errors"]) == 1


# ============================================================================
# 4. System Optimizer Tests
# ============================================================================

def test_system_optimizer_snapshot():
    snapshot = SuperpowerSystemOptimizer.get_performance_snapshot()
    assert "cpu" in snapshot
    assert "memory" in snapshot
    assert "disks" in snapshot
    assert "top_memory_consumers" in snapshot
    assert snapshot["memory"]["total_gb"] > 0


def test_system_optimizer_latency():
    latency = SuperpowerSystemOptimizer.test_latency()
    assert len(latency) >= 1
    assert any("DNS" in item["name"] or "Gateway" in item["name"] for item in latency)


def test_system_optimizer_junk_scan(tmp_path):
    test_dir = tmp_path / "junk_test"
    test_dir.mkdir()
    (test_dir / "temp1.tmp").write_text("junk data", encoding="utf-8")
    (test_dir / "app.log").write_text("log line", encoding="utf-8")

    res = SuperpowerSystemOptimizer.scan_temporary_files(str(test_dir))
    assert res["junk_files_count"] == 2


# ============================================================================
# 5. Tool Registry Integration
# ============================================================================

def test_tool_registry_has_32_tools():
    registry = ToolRegistry()
    tools = registry.get_all_tools()
    assert len(tools) >= 32
    tool_names = [t.name for t in tools]
    assert "deep_research_studio" in tool_names
    assert "orchestrate_complex_goal" in tool_names
    assert "code_studio_builder" in tool_names
    assert "system_super_optimizer" in tool_names


def test_orchestrate_tool_execution():
    registry = ToolRegistry()
    tool = registry.get_tool("orchestrate_complex_goal")
    res = tool.execute(goal="Deploy AI Super-Agent")
    assert res["success"] is True
    assert "pipeline" in res


def test_optimizer_tool_execution():
    registry = ToolRegistry()
    tool = registry.get_tool("system_super_optimizer")
    res = tool.execute(action="snapshot")
    assert res["success"] is True
    assert "performance" in res["diagnostics"]


# ============================================================================
# 6. LLM Rule Engine Superpower Routing
# ============================================================================

def test_rule_engine_superpower_orchestrator_routing():
    llm = LLMClient(provider="rule_engine")
    step = llm.generate_step(
        goal="make this ai agent super power ai agent ever on web with pipeline",
        trajectory_summary="No previous steps executed yet.",
        tool_schemas="",
        os_info={"os": "Windows", "release": "11"}
    )
    assert step["action"] == "orchestrate_complex_goal"
    assert step["is_complete"] is True


def test_rule_engine_deep_research_routing():
    llm = LLMClient(provider="rule_engine")
    step = llm.generate_step(
        goal="do deep research on quantum computing and generate intelligence dossier",
        trajectory_summary="No previous steps executed yet.",
        tool_schemas="",
        os_info={"os": "Windows", "release": "11"}
    )
    assert step["action"] == "deep_research_studio"
    assert step["is_complete"] is True


def test_rule_engine_optimizer_routing():
    llm = LLMClient(provider="rule_engine")
    step = llm.generate_step(
        goal="run system optimizer and pc tuneup",
        trajectory_summary="No previous steps executed yet.",
        tool_schemas="",
        os_info={"os": "Windows", "release": "11"}
    )
    assert step["action"] == "system_super_optimizer"
    assert step["is_complete"] is True
