"""Unit tests for Background AI Swarm & Dynamic Multi-AI Router."""
import pytest
from core.background_ai_swarm import background_ai_swarm
from core.tools.background_ai_tools import ConsultBackgroundAITool

def test_available_providers():
    providers = background_ai_swarm.get_available_providers()
    assert len(providers) >= 5
    provider_ids = [p["id"] for p in providers]
    assert "groq" in provider_ids
    assert "gemini" in provider_ids
    assert "deepseek" in provider_ids
    assert "openai" in provider_ids
    assert "ollama" in provider_ids

def test_background_consult_offline_fallback():
    res = background_ai_swarm.consult(
        query="Plan an autonomous workflow for system diagnostics",
        provider="auto",
        role="planner"
    )
    assert res["success"] is True
    assert "content" in res
    assert len(res["content"]) > 10

def test_background_ai_tool_execution():
    tool = ConsultBackgroundAITool()
    assert tool.name == "consult_background_ai"
    res = tool.execute(query="How to diagnose open network ports?", provider="auto", role="debugger")
    assert res["success"] is True
    assert "output" in res
    assert "Background AI" in res["output"] or "Debugger" in res["output"]
