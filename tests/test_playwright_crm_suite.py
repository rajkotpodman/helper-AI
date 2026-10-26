import os
import pytest
from fastapi.testclient import TestClient
from app import app
from core.playwright_manager import PlaywrightManager
from core.tools.playwright_tools import PlaywrightCodegenTool, PlaywrightWorkflowTool

client = TestClient(app)

def test_playwright_manager_status():
    mgr = PlaywrightManager()
    status = mgr.get_status()
    assert isinstance(status, dict)
    assert "playwright_installed" in status
    assert status["playwright_installed"] is True
    assert "active_codegen" in status

def test_playwright_manager_list_workflows():
    mgr = PlaywrightManager()
    workflows = mgr.list_workflows()
    assert isinstance(workflows, list)
    filenames = [w["filename"] for w in workflows]
    assert "tata_crm_template.py" in filenames

def test_playwright_manager_get_and_save_workflow():
    mgr = PlaywrightManager()
    test_script_name = "pytest_temp_automation"
    test_code = "# Pytest temporary automation script\nprint('Hello from test')\n"
    
    save_result = mgr.save_workflow(test_script_name, test_code)
    assert save_result["status"] == "saved"
    
    loaded = mgr.get_workflow(test_script_name)
    assert loaded["found"] is True
    assert "Hello from test" in loaded["code"]
    
    # Cleanup temp file
    if os.path.exists(save_result["path"]):
        os.remove(save_result["path"])

def test_playwright_codegen_tool():
    tool = PlaywrightCodegenTool()
    res = tool.execute(action="status")
    assert isinstance(res, dict)
    assert res.get("success") is True
    assert res.get("status", {}).get("installed") is True

def test_playwright_workflow_tool():
    tool = PlaywrightWorkflowTool()
    res = tool.execute(action="list")
    assert isinstance(res, dict)
    assert "workflows" in res
    assert any(w["filename"] == "tata_crm_template.py" for w in res["workflows"])

def test_api_playwright_status():
    response = client.get("/api/playwright/status")
    assert response.status_code == 200
    data = response.json()
    assert data["playwright_installed"] is True

def test_api_playwright_workflows():
    response = client.get("/api/playwright/workflows")
    assert response.status_code == 200
    data = response.json()
    assert "workflows" in data
    assert any(w["filename"] == "tata_crm_template.py" for w in data["workflows"])

def test_api_playwright_get_workflow():
    response = client.get("/api/playwright/workflows/tata_crm_template.py")
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert "name" in data["code"]

def test_playwright_batch_execution_mock():
    mgr = PlaywrightManager()
    dummy_name = "test_dummy_batch"
    dummy_code = """
import sys
name = "{{name}}"
mobile = "{{mobile}}"
print(f"Processed: {name} - {mobile}")
"""
    mgr.save_workflow(dummy_name, dummy_code)
    try:
        leads = [
            {"name": "Lead 1", "mobile": "9999900001"},
            {"name": "Lead 2", "mobile": "9999900002"}
        ]
        res = mgr.run_workflow_batch(dummy_name, leads, delay_between_records_s=0.01)
        assert res["success"] is True
        assert res["total_rows"] == 2
        assert res["completed_rows"] == 2
        assert len(res["record_logs"]) == 2
        assert "Lead 1 - 9999900001" in res["record_logs"][0]["output"]
    finally:
        from core.playwright_manager import WORKFLOWS_DIR
        f = WORKFLOWS_DIR / f"{dummy_name}.py"
        if f.exists():
            f.unlink()

def test_self_healing_engine_import_and_helpers():
    from core.self_healing_engine import SmartCRMPage, CRM_SPINNER_SELECTORS
    assert len(CRM_SPINNER_SELECTORS) >= 5
    assert ".siebel-busy-indicator" in CRM_SPINNER_SELECTORS

def test_smart_recorder_code_generation():
    from core.smart_recorder import SmartRecorder
    recorder = SmartRecorder()
    sample_actions = [
        {"action": "goto", "url": "https://crmdms.inservices.tatamotors.com/siebel/app/showroom"},
        {"action": "click", "selector": "#s_swepi_1", "tag": "button", "text": "Submit", "locators": {"id": "#s_swepi_1", "text": "text=Submit"}},
        {"action": "fill", "selector": "input[name='SWEUserName']", "value": "test_user", "tag": "input", "locators": {"css": "input[name='SWEUserName']"}},
        {"action": "press", "selector": "input[name='SWEUserName']", "key": "Enter"}
    ]
    code = recorder.generate_python_script("https://crmdms.inservices.tatamotors.com/siebel/app/showroom", sample_actions, "test_smart_code")
    assert "SmartCRMPage" in code
    assert "crm.smart_goto" in code
    assert "crm.smart_click" in code
    assert "crm.smart_fill" in code
    assert "crm.smart_press" in code
    assert "PROJECT_ROOT" in code

def test_playwright_manager_smart_mode_dispatch():
    mgr = PlaywrightManager()
    status = mgr.get_status()
    assert "smart_recording_active" in status


