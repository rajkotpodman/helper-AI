"""Tests for Anti-Loop Breaker, Multi-Provider LLM Failover, and Google Business Profile Summary."""
import pytest
from unittest.mock import MagicMock, patch
from core.agent import HelperAgent
from core.llm import LLMClient


@pytest.mark.asyncio
async def test_anti_loop_breaker_duplicate_search():
    """Verify that repeating identical search queries triggers the anti-loop breaker and synthesizes summary."""
    llm = LLMClient(provider="rule_engine")
    agent = HelperAgent(llm_client=llm, max_steps=10)

    # Mock llm to repeatedly suggest the exact same search query
    mock_step = {
        "thought": "Searching alternative",
        "action": "search_web",
        "action_args": {"query": "check my google business alternative"},
        "is_complete": False,
        "completion_message": ""
    }
    llm.generate_step = MagicMock(return_value=mock_step)

    events = []
    def on_event(ev_type, data):
        events.append((ev_type, data))

    # Seed initial history with observation
    agent.tools.execute = MagicMock(return_value={
        "success": True,
        "output": "Found Google Business Profile: Aayush Mobile (Verified)"
    })

    result = await agent.run(goal="check my google business and give me summery", on_event=on_event)

    # Must complete successfully rather than hitting 10 max steps in a loop
    assert result["success"] is True
    assert result["steps_executed"] < 10
    # Verify anti-loop status update was emitted
    status_messages = [d.get("message", "") for t, d in events if t == "status_update"]
    assert any("Anti-Loop Breaker" in msg for msg in status_messages)
    assert "Google Business" in result["final_message"]


@pytest.mark.asyncio
async def test_anti_loop_breaker_identical_action_repetition():
    """Verify that repeated consecutive tool actions trigger the loop breaker and conclude."""
    llm = LLMClient(provider="rule_engine")
    agent = HelperAgent(llm_client=llm, max_steps=8)

    mock_step = {
        "thought": "Reading page content repeatedly",
        "action": "browser_automation",
        "action_args": {"action": "fetch_full_page"},
        "is_complete": False,
        "completion_message": ""
    }
    llm.generate_step = MagicMock(return_value=mock_step)

    agent.tools.execute = MagicMock(return_value={
        "success": True,
        "output": "Webpage content with 3 businesses: Aayush Mobile, AI Aayush Institute, L. O. C. Cyber"
    })

    result = await agent.run(goal="check my google business and give me summery")

    assert result["success"] is True
    assert result["steps_executed"] <= 3
    assert "3 registered businesses" in result["final_message"] or "Aayush Mobile" in result["final_message"]


def test_rule_engine_google_business_summary_synthesis():
    """Verify _rule_engine_step extracts Google Business profiles from trajectory and generates summary."""
    llm = LLMClient(provider="rule_engine")
    sample_trajectory = (
        "Step 1: Opened 'https://business.google.com/locations'. Result: Page Title: 'Businesses'\n"
        "Business Profile Manager Businesses Reviews Linked accounts Settings Support Create group 3 businesses 100% verified\n"
        "Businesses All (3) Add business Store code Business Status\n"
        "'Aayush Mobile And Computer Accessories Smart Watch Rajkot'\n"
        "'AI Aayush Institute'\n"
        "'L. O. C. Cyber Mobile World'\n"
    )

    decision = llm._rule_engine_step("check my google business and give me summery", sample_trajectory)

    assert decision["is_complete"] is True
    assert decision["action"] == "none"
    assert "Google Business Profile Executive Summary" in decision["completion_message"]
    assert "Aayush Mobile" in decision["completion_message"]
    assert "100% verified" in decision["completion_message"].lower() or "3" in decision["completion_message"]


def test_rule_engine_no_loop_on_search_web():
    """Verify _rule_engine_step does NOT repeat search_web if already executed."""
    llm = LLMClient(provider="rule_engine")
    sample_trajectory = (
        "Step 1: Action search_web(query='test alternative'). Result: 6 Best Google Business Website Alternatives\n"
    )

    decision = llm._rule_engine_step("check my google business and give me summery", sample_trajectory)

    # It must NOT return search_web again!
    assert decision["action"] != "search_web"
    assert decision["is_complete"] is True


def test_multi_provider_failover_gemini_to_groq():
    """Verify that when Gemini fails (e.g. 429 quota), LLMClient seamlessly fails over to Groq."""
    llm = LLMClient(provider="gemini")

    # Mock _call_gemini to simulate 429 Quota Exceeded error
    llm._call_gemini = MagicMock(side_effect=RuntimeError("HTTP 429: Resource has been exhausted (e.g. check quota)"))

    # Mock _call_groq to succeed
    expected_step = {
        "thought": "Groq decided next step",
        "action": "browser_automation",
        "action_args": {"action": "fetch_full_page"},
        "is_complete": False,
        "completion_message": ""
    }
    llm._call_groq = MagicMock(return_value=expected_step)

    with patch.dict("os.environ", {"GROQ_API_KEY": "gsk_test123"}):
        step = llm.generate_step(
            goal="check my google business and give me summery",
            trajectory_summary="No previous steps.",
            tool_schemas="{}",
            os_info={"os_name": "Windows"}
        )

    assert "Failover to Groq" in step["thought"]
    assert step["action"] == "browser_automation"
    llm._call_gemini.assert_called_once()
    llm._call_groq.assert_called_once()
