"""Unit tests for HelperAgent autonomous loop."""
import asyncio
import pytest
from core.agent import HelperAgent
from core.llm import LLMClient

@pytest.mark.asyncio
async def test_agent_rule_engine_execution():
    llm = LLMClient(provider="rule_engine")
    agent = HelperAgent(llm_client=llm, max_steps=5)

    events_received = []
    def on_event(ev_type, data):
        events_received.append(ev_type)

    result = await agent.run(goal="Check PC health, CPU and RAM specs", on_event=on_event)

    assert result["success"] is True
    assert "started" in events_received
    assert "step_start" in events_received
    assert "thought" in events_received
    assert "completed" in events_received
    assert len(result["history"]) >= 1

@pytest.mark.asyncio
async def test_agent_cancel_signal():
    llm = LLMClient(provider="rule_engine")
    agent = HelperAgent(llm_client=llm, max_steps=10)

    # Trigger cancel before run
    agent.cancel()
    result = await agent.run(goal="Long running task")

    assert result["success"] is False
    assert "cancelled" in result["final_message"].lower()

@pytest.mark.asyncio
async def test_agent_safe_mode_blocking():
    llm = LLMClient(provider="rule_engine")
    agent = HelperAgent(llm_client=llm, safe_mode=True)

    # Mock step decision with dangerous command
    llm.generate_step = lambda **kwargs: {
        "thought": "Dangerous command",
        "action": "execute_powershell",
        "action_args": {"command": "rmdir /s /q C:\\Test"},
        "is_complete": False,
        "completion_message": ""
    }

    result = await agent.run(goal="Delete folder")
    # Step should be blocked by safe mode
    assert any("blocked by safe mode" in step["result"].lower() for step in result["history"])
