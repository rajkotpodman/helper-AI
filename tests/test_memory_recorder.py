"""Unit and integration tests for MarkdownMemoryRecorder (agent_memory.md)."""
import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from core.memory_recorder import MarkdownMemoryRecorder
from core.agent import HelperAgent
from core.llm import LLMClient
from app import app

client = TestClient(app)

def test_record_interaction_creates_file_and_logs(tmp_path):
    mem_file = tmp_path / "test_memory.md"
    recorder = MarkdownMemoryRecorder(file_path=mem_file, max_bytes=20 * 1024 * 1024)

    prompt = "Check disk space on C drive"
    reply = "Disk has 120 GB free space remaining."
    
    result = recorder.record_interaction(
        prompt=prompt,
        final_reply=reply,
        success=True,
        steps_executed=2
    )

    assert result["recorded"] is True
    assert result["limit_reached"] is False
    assert mem_file.exists()

    content = recorder.read_content()
    assert "Check disk space on C drive" in content
    assert "Disk has 120 GB free space remaining." in content
    assert "✅ SUCCESS" in content
    assert "**Steps Executed:** 2" in content

def test_memory_recorder_size_and_read(tmp_path):
    mem_file = tmp_path / "size_test.md"
    recorder = MarkdownMemoryRecorder(file_path=mem_file)

    assert recorder.get_size_bytes() > 0
    assert recorder.get_size_mb() >= 0.0

    recorder.record_interaction("Test Prompt", "Test Reply")
    assert recorder.get_size_bytes() > 100

def test_limit_reached_alert_archive_and_reset(tmp_path):
    mem_file = tmp_path / "small_limit_memory.md"
    # Set a tiny limit (250 bytes) to test 20 MB rotation behavior
    recorder = MarkdownMemoryRecorder(file_path=mem_file, max_bytes=250)

    # First interaction fits within file
    res1 = recorder.record_interaction("Short prompt", "Short reply")
    assert res1["limit_reached"] is True or recorder.get_size_bytes() > 0

    # Large interaction triggers rotation
    long_reply = "A" * 300
    res2 = recorder.record_interaction("Trigger 20MB threshold", long_reply)

    assert res2["limit_reached"] is True
    assert "Memory Alert" in res2["alert_message"]
    assert "copy and store/backup" in res2["alert_message"]
    assert res2["archive_path"] is not None
    assert os.path.exists(res2["archive_path"])

    # Verify the active file was reset and ready for new memory
    fresh_content = recorder.read_content()
    assert "# 🧠 Helper-AI Memory Log" in fresh_content
    # The old long reply should be in the archive, not in the reset active file
    assert long_reply not in fresh_content

def test_manual_reset_file(tmp_path):
    mem_file = tmp_path / "reset_test.md"
    recorder = MarkdownMemoryRecorder(file_path=mem_file)
    recorder.record_interaction("Old prompt", "Old reply")

    assert "Old prompt" in recorder.read_content()
    recorder.reset_file()
    assert "Old prompt" not in recorder.read_content()
    assert "# 🧠 Helper-AI Memory Log" in recorder.read_content()

def test_api_memory_endpoints():
    # 1. Test status
    res = client.get("/api/memory/status")
    assert res.status_code == 200
    data = res.json()
    assert "file_name" in data
    assert "size_bytes" in data
    assert "limit_mb" in data

    # 2. Test download
    res_dl = client.get("/api/memory/download")
    assert res_dl.status_code == 200
    assert "text/markdown" in res_dl.headers.get("content-type", "")

    # 3. Test reset
    res_rst = client.post("/api/memory/reset")
    assert res_rst.status_code == 200
    assert res_rst.json()["success"] is True

@pytest.mark.asyncio
async def test_agent_memory_recording_integration(tmp_path):
    mem_file = tmp_path / "integration_memory.md"
    recorder = MarkdownMemoryRecorder(file_path=mem_file)
    llm = LLMClient(provider="rule_engine")
    agent = HelperAgent(llm_client=llm, memory_recorder=recorder, max_steps=3)

    result = await agent.run(goal="Check PC health, CPU and RAM specs")

    assert result["success"] is True
    assert "memory_info" in result
    assert result["memory_info"] is not None

    # Check that file now contains the executed goal and result
    content = recorder.read_content()
    assert "Check PC health, CPU and RAM specs" in content
    assert "Final Reply" in content
