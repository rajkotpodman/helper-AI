"""Unit tests for Dolphin-2.9-Llama3 and Ollama Auto-Setup Engine."""
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app import app
from core.auto_setup_ollama import OllamaAutoSetup
from core.llm import LLMClient


@pytest.fixture
def client():
    return TestClient(app)


def test_ollama_status_api(client):
    """Test the /api/ollama/status endpoint."""
    response = client.get("/api/ollama/status")
    assert response.status_code == 200
    data = response.json()
    assert "installed" in data
    assert "running" in data
    assert "models" in data
    assert "dolphin_ready" in data
    assert "active_model" in data


def test_system_status_reports_ollama_model(client):
    """Test that /api/system-status includes ollama_model configuration."""
    response = client.get("/api/system-status")
    assert response.status_code == 200
    data = response.json()
    assert "ollama_model" in data
    assert "provider" in data


def test_llm_client_dolphin_defaults():
    """Verify LLMClient defaults to dolphin-llama3 when provider is ollama."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "OLLAMA_MODEL": "dolphin-llama3"}):
        client = LLMClient(provider="ollama")
        assert client.provider == "ollama"
        assert client.model == "dolphin-llama3"


def test_auto_setup_detection():
    """Verify that OllamaAutoSetup detects executable or AppData path."""
    installed = OllamaAutoSetup.is_ollama_installed()
    # On this development machine, Ollama is installed in AppData
    assert installed is True
    path = OllamaAutoSetup.get_ollama_path()
    assert path is not None
    assert "ollama" in path.lower()


def test_model_resolution_matches_dolphin():
    """Verify LLMClient._resolve_ollama_model selects dolphin when configured or requested."""
    client = LLMClient(provider="ollama", model="dolphin-llama3")
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "models": [
                {"name": "llama3.2:3b"},
                {"name": "dolphin-llama3:latest"},
                {"name": "qwen2.5:1.5b"}
            ]
        }
        mock_get.return_value = mock_resp
        resolved = client._resolve_ollama_model("http://localhost:11434")
        assert "dolphin" in resolved.lower()
