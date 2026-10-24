"""Unit tests for Anthropic and Claude integration in Helper-AI."""
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from server import app
from core.llm import LLMClient
from core.background_ai_swarm import BackgroundAISwarm
from core.tools.background_ai_tools import ConsultBackgroundAITool

client = TestClient(app)

def test_settings_anthropic_persistence():
    """Verify /api/settings reads and updates Anthropic API key and model."""
    orig_resp = client.get("/api/settings")
    assert orig_resp.status_code == 200
    orig_data = orig_resp.json()
    assert "anthropic_key" in orig_data
    assert "anthropic_model" in orig_data

    # Update via API
    try:
        update_payload = {
            "provider": "anthropic",
            "anthropic_key": "sk-ant-test-sample-key",
            "anthropic_model": "claude-3-5-sonnet-20241022"
        }
        post_resp = client.post("/api/settings", json=update_payload)
        assert post_resp.status_code == 200
        assert post_resp.json().get("success") is True

        # Check updated settings
        get_resp = client.get("/api/settings")
        assert get_resp.json().get("anthropic_key") == "sk-ant-test-sample-key"
        assert get_resp.json().get("provider") == "anthropic"
    finally:
        # Restore original settings
        client.post("/api/settings", json={
            "provider": orig_data.get("provider"),
            "anthropic_key": orig_data.get("anthropic_key"),
            "anthropic_model": orig_data.get("anthropic_model")
        })

def test_llm_client_anthropic_init():
    """Test LLMClient initializes with Anthropic provider and default model."""
    llm = LLMClient(provider="anthropic", api_key="sk-ant-test-123")
    assert llm.provider == "anthropic"
    assert llm.api_key == "sk-ant-test-123"
    assert "claude" in llm.model.lower()

def test_llm_client_anthropic_mock_success():
    """Test LLMClient _call_anthropic parses response successfully."""
    llm = LLMClient(provider="anthropic", api_key="sk-ant-dummy")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "content": [
            {
                "type": "text",
                "text": '{"thought": "Checking environment", "action": "none", "is_complete": true, "completion_message": "All good"}'
            }
        ]
    }
    with patch.object(llm._session, "post", return_value=mock_resp):
        res = llm._call_anthropic("You are Helper", "Hello")
        assert res.get("is_complete") is True
        assert res.get("completion_message") == "All good"

def test_background_swarm_anthropic():
    """Test BackgroundAISwarm lists Anthropic Claude and supports querying."""
    swarm = BackgroundAISwarm.get_instance()
    providers = swarm.get_available_providers()
    anthropic_prov = next((p for p in providers if p["id"] == "anthropic"), None)
    assert anthropic_prov is not None
    assert "Claude" in anthropic_prov["name"]

def test_consult_background_ai_tool_enum():
    """Test ConsultBackgroundAITool allows anthropic and claude providers."""
    tool = ConsultBackgroundAITool()
    enum_vals = tool.parameters["properties"]["provider"]["enum"]
    assert "anthropic" in enum_vals
    assert "claude" in enum_vals
