"""Unit and integration tests for PermissionManager and 1-Click HITL authorization."""
import asyncio
import pytest
from fastapi.testclient import TestClient
from core.permissions import PermissionManager
from core.agent import HelperAgent
from core.llm import LLMClient
from app import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_permission_manager_approval():
    pm = PermissionManager(unrestricted=False)
    
    async def simulate_user_approval():
        await asyncio.sleep(0.05)
        pending = pm.get_pending()
        assert pending is not None
        req_id = pending["request_id"]
        assert pm.respond(req_id, approved=True) is True

    user_task = asyncio.create_task(simulate_user_approval())
    approved = await pm.request_permission("execute_powershell", "Format disk test", timeout_seconds=2.0)
    await user_task

    assert approved is True
    assert pm.get_pending() is None

@pytest.mark.asyncio
async def test_permission_manager_denial():
    pm = PermissionManager(unrestricted=False)
    
    async def simulate_user_denial():
        await asyncio.sleep(0.05)
        pending = pm.get_pending()
        assert pending is not None
        req_id = pending["request_id"]
        assert pm.respond(req_id, approved=False) is True

    user_task = asyncio.create_task(simulate_user_denial())
    approved = await pm.request_permission("draft_social_post", "Publish Tweet", timeout_seconds=2.0)
    await user_task

    assert approved is False
    assert pm.get_pending() is None

@pytest.mark.asyncio
async def test_permission_manager_timeout():
    pm = PermissionManager(unrestricted=False)
    # Test short timeout auto-deny
    approved = await pm.request_permission("unknown_action", "Will timeout", timeout_seconds=0.1)
    assert approved is False
    assert pm.get_pending() is None

@pytest.mark.asyncio
async def test_permission_manager_cancel_all():
    pm = PermissionManager(unrestricted=False)
    
    async def wait_req():
        return await pm.request_permission("action", "test", timeout_seconds=5.0)

    task = asyncio.create_task(wait_req())
    await asyncio.sleep(0.05)
    assert pm.get_pending() is not None
    pm.cancel_all()
    approved = await task
    assert approved is False

@pytest.mark.asyncio
async def test_permission_manager_unrestricted_mode():
    pm = PermissionManager(unrestricted=True)
    assert pm.is_unrestricted() is True
    approved = await pm.request_permission("del /f *", "Dangerous unrestricted test", timeout_seconds=0.5)
    assert approved is True
    assert pm.get_pending() is None

def test_api_permission_endpoints():
    # 1. Test get pending when empty
    res = client.get("/api/permission/pending")
    assert res.status_code == 200
    assert "pending" in res.json()

    # 2. Test respond to non-existent request
    res2 = client.post("/api/permission/respond", json={"request_id": "nonexistent", "approved": True})
    assert res2.status_code == 200
    assert res2.json()["success"] is False

from core.memory_recorder import MarkdownMemoryRecorder

@pytest.mark.asyncio
async def test_agent_human_in_the_loop_permission_flow(tmp_path):
    pm = PermissionManager(unrestricted=False)
    llm = LLMClient(provider="rule_engine")
    mem_file = tmp_path / "perm_mem.md"
    temp_recorder = MarkdownMemoryRecorder(file_path=mem_file)
    agent = HelperAgent(llm_client=llm, permission_manager=pm, memory_recorder=temp_recorder, max_steps=1)
    agent.unrestricted_mode = False

    # Mock LLM decision requiring permission
    llm.generate_step = lambda **kwargs: {
        "thought": "Publish social post",
        "action": "browser_automation",
        "action_args": {"action": "draft_social_post", "platform": "x", "post_text": "Test post", "open_in_system_browser": False},
        "is_complete": False,
        "completion_message": ""
    }

    # Simulate user approval in background
    async def auto_approve():
        for _ in range(20):
            await asyncio.sleep(0.05)
            pending = pm.get_pending()
            if pending:
                pm.respond(pending["request_id"], approved=True)
                break

    approve_task = asyncio.create_task(auto_approve())
    result = await agent.run(goal="Post to X")
    await approve_task

    assert len(result["history"]) >= 1
    # Check that tool was executed after approval
    assert any("prepared draft post" in str(step["result"]).lower() for step in result["history"])
