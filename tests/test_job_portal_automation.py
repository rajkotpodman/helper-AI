import os
import pytest
from fastapi.testclient import TestClient
from app import app
from core.job_portal_automation import JobPortalAutomation
from core.tools.job_portal_tools import JobPortalTool

client = TestClient(app)

def test_job_portal_locate_and_parse_cv():
    engine = JobPortalAutomation()
    profile = engine.parse_cv_details()
    assert profile["success"] is True
    assert "Jignesh" in profile["full_name"]
    assert profile["email"] == "oo71097145198@gmail.com"
    assert "9898048483" in profile["phone"]
    assert len(profile["skills"]) > 0
    assert os.path.exists(profile["cv_path"])

def test_job_portals_list():
    engine = JobPortalAutomation()
    portals = engine.get_portals()
    assert len(portals) == 10
    names = [p["name"] for p in portals]
    assert "Internshala" in names
    assert "Indeed India" in names
    assert "Naukri.com" in names
    assert "Upwork" in names

def test_job_portal_tool():
    tool = JobPortalTool()
    # Test parse_cv action
    res_cv = tool.execute(action="parse_cv")
    assert res_cv["success"] is True
    assert "Jignesh" in res_cv["output"]
    
    # Test status action
    res_status = tool.execute(action="status")
    assert res_status["success"] is True
    assert "10 portals" in res_status["output"]

def test_api_job_portals_status():
    response = client.get("/api/job-portals/status")
    assert response.status_code == 200
    data = response.json()
    assert "candidate" in data
    assert "Jignesh" in data["candidate"]["full_name"]
    assert len(data["portals"]) == 10
