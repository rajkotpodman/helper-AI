"""Tests for server.py and modernized Helper-AI cyber web dashboard."""
import pytest
from fastapi.testclient import TestClient
from server import app as server_app
from app import app as main_app

@pytest.fixture
def client():
    return TestClient(server_app)

@pytest.fixture
def main_client():
    return TestClient(main_app)

def test_server_index_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Helper-AI" in response.text
    assert "Autonomous PC Control & Internet Agent" in response.text
    assert "styles.css" in response.text
    assert "app.js" in response.text

def test_server_system_status(client):
    response = client.get("/api/system-status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "cpu_percent" in data
    assert "ram_percent" in data
    assert "tools_registered" in data
    assert data["tools_registered"] > 0

def test_server_quick_ideas(client):
    response = client.get("/api/quick-ideas")
    assert response.status_code == 200
    data = response.json()
    assert "ideas" in data
    assert len(data["ideas"]) >= 5
    ids = [item["id"] for item in data["ideas"]]
    assert "google_blogs" in ids
    assert "pc_health" in ids

def test_server_static_assets(client):
    css_res = client.get("/static/css/styles.css")
    assert css_res.status_code == 200
    assert "cyberDark" in css_res.text or "backdrop-filter" in css_res.text

    js_res = client.get("/static/js/app.js")
    assert js_res.status_code == 200
    assert "executeGoal" in js_res.text

def test_server_execute_validation(client):
    # Empty goal should return 400
    res = client.post("/api/execute", json={"goal": "  "})
    assert res.status_code == 400

def test_main_app_endpoint_parity(main_client):
    res_status = main_client.get("/api/system-status")
    assert res_status.status_code == 200
    res_ideas = main_client.get("/api/quick-ideas")
    assert res_ideas.status_code == 200
    res_index = main_client.get("/")
    assert res_index.status_code == 200
    assert "Helper-AI" in res_index.text
