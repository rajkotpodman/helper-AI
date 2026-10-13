"""Tests for defensive security baseline auditing tool and ethical diagnostics."""
import pytest
from core.tools import ToolRegistry
from core.tools.system_tools import AuditSecurityBaselineTool
from core.llm import LLMClient


@pytest.fixture
def registry():
    return ToolRegistry()


def test_registry_contains_25_tools(registry):
    tools = registry.get_all_tools()
    assert len(tools) >= 25
    tool_names = [t.name for t in tools]
    assert "audit_security_baseline" in tool_names


def test_audit_security_baseline_tool_execution(registry):
    tool = registry.get_tool("audit_security_baseline")
    assert tool is not None
    assert tool.name == "audit_security_baseline"

    # Test firewall check
    result = tool.execute(target="firewall", save_report=False)
    assert result["success"] is True
    assert "firewall" in result["findings"]
    assert "Defensive Security & System Hardening Baseline Report" in result["output"]


def test_audit_security_baseline_all_targets(registry):
    tool = registry.get_tool("audit_security_baseline")
    result = tool.execute(target="all", save_report=False)
    assert result["success"] is True
    assert "Executive Hardening Recommendations" in result["output"]
    assert "firewall" in result["findings"]
    assert "ports" in result["findings"]
    assert "services" in result["findings"]


def test_rule_engine_routing_for_security_audit():
    llm = LLMClient(provider="rule_engine")
    step = llm.generate_step(
        goal="Run a complete defensive security audit of my PC and check open ports and firewall",
        trajectory_summary="No previous steps executed yet.",
        tool_schemas="",
        os_info={"os": "Windows", "release": "11"}
    )
    assert step["action"] == "audit_security_baseline"
    assert step["is_complete"] is True
