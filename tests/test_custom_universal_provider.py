"""Tests for Universal / Custom AI Provider Integration across Helper-AI."""
import os
import json
import pytest
from unittest.mock import MagicMock, patch
from core.llm import LLMClient
from app import app
from fastapi.testclient import TestClient


def test_custom_provider_initialization():
    """Verify LLMClient properly initializes custom AI provider and handles parameters."""
    client = LLMClient(
        provider="custom",
        api_key="sk-custom-secret-key",
        model="meta-llama/llama-3.3-70b-instruct",
        base_url="https://openrouter.ai/api/v1"
    )
    assert client.provider == "custom"
    assert client.api_key == "sk-custom-secret-key"
    assert client.model == "meta-llama/llama-3.3-70b-instruct"
    assert client.base_url == "https://openrouter.ai/api/v1"


def test_custom_provider_test_connection_unconfigured():
    """Verify test_connection returns 'unconfigured' when no custom URL is supplied."""
    with patch.dict(os.environ, {"CUSTOM_LLM_URL": "", "UNIVERSAL_LLM_URL": ""}, clear=False):
        client = LLMClient(provider="custom", api_key="", base_url="")
        result = client.test_connection(provider="custom")
        assert result["provider"] == "custom"
        assert result["status"] == "unconfigured"


def test_custom_provider_test_connection_success_via_models():
    """Verify test_connection probes /models and returns 'connected'."""
    client = LLMClient(
        provider="custom",
        api_key="sk-my-key",
        base_url="https://api.mistral.ai/v1"
    )
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": [{"id": "mistral-large-latest"}]}

    with patch.object(client._session, "get", return_value=mock_resp):
        res = client.test_connection(provider="custom")
        assert res["provider"] == "custom"
        assert res["status"] == "connected"
        assert "connected successfully" in res["message"]


def test_custom_provider_openai_compatible_call():
    """Verify _call_custom_ai works with any OpenAI-compatible endpoint (OpenRouter, Mistral, Grok, vLLM)."""
    client = LLMClient(
        provider="custom",
        api_key="sk-or-test-key",
        base_url="https://openrouter.ai/api/v1",
        model="anthropic/claude-3.5-sonnet"
    )

    expected_output = {
        "thought": "Using Universal AI to inspect system baseline",
        "action": "audit_security_baseline",
        "action_args": {"target": "firewall"},
        "is_complete": False,
        "completion_message": ""
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(expected_output)
                }
            }
        ]
    }

    with patch("openai.OpenAI", side_effect=Exception("Simulate direct HTTP fallback")):
        with patch.object(client._session, "post", return_value=mock_resp):
            step = client._call_custom_ai("System prompt", "Goal: check firewall")
            assert step["action"] == "audit_security_baseline"
            assert step["action_args"]["target"] == "firewall"
            assert step["is_complete"] is False


def test_custom_provider_anthropic_claude_call():
    """Verify _call_custom_ai formats Anthropic headers and payloads for Claude endpoints."""
    client = LLMClient(
        provider="custom",
        api_key="sk-ant-test-key",
        base_url="https://api.anthropic.com/v1",
        model="claude-3-5-sonnet-20241022"
    )

    expected_output = {
        "thought": "Claude analyzing goal and returning step",
        "action": "fast_app_operate",
        "action_args": {"target": "Calculator", "action": "equals"},
        "is_complete": True,
        "completion_message": "Calculated value successfully"
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "content": [
            {
                "type": "text",
                "text": json.dumps(expected_output)
            }
        ]
    }

    with patch.object(client._session, "post", return_value=mock_resp) as mock_post:
        step = client._call_custom_ai("System prompt", "Goal: calculate sum")
        assert step["action"] == "fast_app_operate"
        assert step["is_complete"] is True
        # Verify Anthropic specific headers were sent
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["headers"]["x-api-key"] == "sk-ant-test-key"
        assert "anthropic-version" in call_kwargs["headers"]


def test_custom_settings_api_persistence():
    """Verify /api/settings accepts custom provider configuration and persists all values."""
    client = TestClient(app)
    resp = client.post("/api/settings", json={
        "provider": "custom",
        "custom_name": "My LM Studio Server",
        "custom_url": "http://192.168.1.100:1234/v1",
        "custom_key": "local-token-xyz",
        "custom_model": "mistral-7b-instruct-v0.3",
        "safe_mode": False
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert os.environ.get("LLM_PROVIDER") == "custom"
    assert os.environ.get("CUSTOM_LLM_NAME") == "My LM Studio Server"
    assert os.environ.get("CUSTOM_LLM_URL") == "http://192.168.1.100:1234/v1"
    assert os.environ.get("CUSTOM_LLM_KEY") == "local-token-xyz"
    assert os.environ.get("CUSTOM_LLM_MODEL") == "mistral-7b-instruct-v0.3"
