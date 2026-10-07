"""Integration tests for FastAPI dashboard endpoints."""
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_api_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "is_running" in data
    assert "tools_count" in data
    assert data["tools_count"] > 0

def test_api_tools():
    response = client.get("/api/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    tool_names = [t["name"] for t in data["tools"]]
    assert "execute_powershell" in tool_names
    assert "get_system_health" in tool_names
    assert "write_file" in tool_names

def test_api_metrics():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "goals" in data
    assert "tools" in data
    assert "system_telemetry" in data

def test_api_audit():
    response = client.get("/api/audit")
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert isinstance(data["events"], list)

def test_api_export():
    response = client.get("/api/export?format=json")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
