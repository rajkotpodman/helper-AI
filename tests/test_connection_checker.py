"""Tests for Helper-AI Connection Diagnostics and Health Engine."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from core.connection_checker import ConnectionChecker, connection_checker
from core.tools.system_tools import CheckConnectionsTool
from core.tools import ToolRegistry
from core.translator import GoogleTranslator
from core.llm import LLMClient
from server import app


def test_connection_checker_singleton():
    c1 = ConnectionChecker.get_instance()
    c2 = ConnectionChecker.get_instance()
    assert c1 is c2
    assert c1 is connection_checker


def test_check_internet_real_or_mock():
    res = connection_checker.check_internet(timeout=3.0)
    assert "status" in res
    assert "latency_ms" in res
    assert res["status"] in ("connected", "degraded", "disconnected")
    assert isinstance(res["latency_ms"], (int, float))


def test_check_translation():
    res = connection_checker.check_translation(timeout=3.0)
    assert res["name"] == "google_translate"
    assert "status" in res
    assert "latency_ms" in res
    assert res["status"] in ("connected", "degraded", "error")


def test_check_llm_providers():
    gemini_res = connection_checker.check_llm("gemini")
    assert "status" in gemini_res
    assert gemini_res["provider"] == "gemini"

    groq_res = connection_checker.check_llm("groq")
    assert "status" in groq_res
    assert groq_res["provider"] == "groq"

    ollama_res = connection_checker.check_llm("ollama")
    assert "status" in ollama_res
    assert ollama_res["provider"] == "ollama"


def test_check_chrome():
    res = connection_checker.check_chrome()
    assert res["name"] == "chrome_browser"
    assert "status" in res
    assert "port_9222_open" in res


def test_check_mcp():
    res = connection_checker.check_mcp()
    assert res["name"] == "mcp_servers"
    assert "status" in res
    assert "servers_count" in res


def test_check_websocket_backend():
    res = connection_checker.check_websocket_backend()
    assert res["name"] == "websocket_server"
    assert "status" in res


def test_check_all():
    res = connection_checker.check_all(timeout=3.0)
    assert "timestamp" in res
    assert "duration_ms" in res
    assert res["total_checked"] >= 7
    assert "connections" in res
    assert "internet" in res["connections"]
    assert "google_translate" in res["connections"]


def test_check_twice_execution():
    """Validates the double-pass check, stability score, and comparison output."""
    res = connection_checker.check_twice(timeout=3.0)
    assert res["success"] is True
    assert res["pass_count"] == 2
    assert "stability_score_pct" in res
    assert res["stability_score_pct"] >= 0.0
    assert "pass_1" in res
    assert "pass_2" in res
    assert "comparison" in res
    assert "summary_markdown" in res
    assert "### ⚡ Helper-AI Double-Pass Connection Diagnostic Report" in res["summary_markdown"]


def test_check_connections_tool():
    """Validates CheckConnectionsTool registered in ToolRegistry."""
    registry = ToolRegistry()
    tool = registry.get_tool("check_connections")
    assert tool is not None
    assert isinstance(tool, CheckConnectionsTool)

    # Pass count 1
    res1 = tool.execute(pass_count=1)
    assert res1["success"] is True
    assert res1["pass_count"] == 1

    # Pass count 2 (double check)
    res2 = tool.execute(pass_count=2)
    assert res2["success"] is True
    assert res2["pass_count"] == 2
    assert "stability_score_pct" in res2
    assert "summary" in res2


def test_api_connections_check_endpoint():
    """Validates FastAPI /api/connections/check and /api/check-connections."""
    client = TestClient(app)

    # Double check (default pass_count=2)
    resp = client.get("/api/connections/check?pass_count=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["pass_count"] == 2
    assert "stability_score_pct" in data

    # Single check alias
    resp2 = client.get("/api/check-connections?pass_count=1")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert "total_checked" in data2


def test_translator_connection_pooling_and_extraction():
    """Validates GoogleTranslator pooled session and multi-type parsing."""
    t = GoogleTranslator.get_instance()
    assert hasattr(t, "_session")
    check = t.check_connection(timeout=3.0)
    assert "status" in check
    assert "latency_ms" in check


def test_llm_client_connection_test():
    """Validates LLMClient test_connection method for offline/ready states."""
    client = LLMClient(provider="rule_engine")
    res = client.test_connection()
    assert res["status"] == "ready"
