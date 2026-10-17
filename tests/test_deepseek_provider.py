"""Tests for DeepSeek LLM Provider Integration across Helper-AI."""
import os
import json
import pytest
from unittest.mock import MagicMock, patch
from core.llm import LLMClient
from app import app
from fastapi.testclient import TestClient


def test_deepseek_initialization():
    """Verify LLMClient properly initializes DeepSeek provider and model defaults."""
    client = LLMClient(provider="deepseek", api_key="sk-test-deepseek-key")
    assert client.provider == "deepseek"
    assert client.api_key == "sk-test-deepseek-key"
    assert client.model == "deepseek-chat"


def test_deepseek_custom_model_and_url():
    """Verify LLMClient accepts custom models (e.g. deepseek-reasoner) and custom base_urls."""
    client = LLMClient(
        provider="deepseek",
        api_key="sk-test-deepseek-key",
        model="deepseek-reasoner",
        base_url="https://api.deepseek.com/v1"
    )
    assert client.provider == "deepseek"
    assert client.model == "deepseek-reasoner"
    assert client.base_url == "https://api.deepseek.com/v1"


def test_deepseek_test_connection_unconfigured():
    """Verify test_connection returns 'unconfigured' when DEEPSEEK_API_KEY is missing."""
    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}, clear=False):
        client = LLMClient(provider="deepseek", api_key="")
        result = client.test_connection(provider="deepseek")
        assert result["provider"] == "deepseek"
        assert result["status"] == "unconfigured"


def test_deepseek_test_connection_success():
    """Verify test_connection returns 'connected' on HTTP 200 from DeepSeek /models."""
    client = LLMClient(provider="deepseek", api_key="sk-valid-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": [{"id": "deepseek-chat"}, {"id": "deepseek-reasoner"}]}

    with patch.object(client._session, "get", return_value=mock_resp):
        res = client.test_connection(provider="deepseek")
        assert res["provider"] == "deepseek"
        assert res["status"] == "connected"
        assert "DeepSeek API connected" in res["message"]


def test_deepseek_call_json_mode():
    """Verify _call_deepseek formats system and user prompts and parses JSON response."""
    client = LLMClient(provider="deepseek", api_key="sk-valid-key", model="deepseek-chat")

    expected_output = {
        "thought": "Operating Notepad using saved App Memory profile",
        "action": "fast_app_operate",
        "action_args": {"target": "Notepad", "action": "save"},
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

    # Simulate OpenAI SDK raising ImportError or fallback to _session.post
    with patch("openai.OpenAI", side_effect=Exception("Use HTTP fallback")):
        with patch.object(client._session, "post", return_value=mock_resp):
            step = client._call_deepseek("System instructions", "User goal: save Notepad")
            assert step["action"] == "fast_app_operate"
            assert step["action_args"]["target"] == "Notepad"
            assert step["is_complete"] is False


def test_deepseek_settings_api():
    """Verify /api/settings accepts deepseek_key and persists it."""
    client = TestClient(app)
    resp = client.post("/api/settings", json={
        "provider": "deepseek",
        "deepseek_key": "sk-new-deepseek-token",
        "safe_mode": False
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert os.environ.get("DEEPSEEK_API_KEY") == "sk-new-deepseek-token"
    assert os.environ.get("LLM_PROVIDER") == "deepseek"
