"""Comprehensive Automated Verification Test Suite for Pasted Screenshot Analysis in Helper-AI.

Tests:
1. Base64 screenshot saving & Pillow metadata extraction
2. Active Windows desktop context extraction
3. Multimodal Vision Reasoning & Forensic Analysis
4. End-to-End Agent run with attached screenshot payload
5. FastAPI /api/vision/analyze and /api/execute endpoints
"""

import io
import base64
import pytest
from pathlib import Path
from PIL import Image
from fastapi.testclient import TestClient

from app import app
from core.vision_engine import VisionEngine, vision_engine
from core.agent import HelperAgent
from core.llm import LLMClient


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def sample_image_base64():
    """Generates a valid test screenshot base64 data URL."""
    img = Image.new("RGB", (640, 480), color=(20, 24, 39))  # Dark mode cyber background
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


def test_vision_engine_save_base64_image(sample_image_base64):
    """Test 1: Verify VisionEngine correctly decodes, saves and extracts visual metadata."""
    res = vision_engine.save_base64_image(sample_image_base64, "unit_test_screenshot.png")
    assert res["success"] is True
    assert res["width"] == 640
    assert res["height"] == 480
    assert res["format"] == "PNG"
    assert res["theme"] == "Dark Mode"
    assert Path(res["file_path"]).exists()


def test_vision_engine_desktop_context():
    """Test 2: Verify desktop context extraction returns active window and process."""
    ctx = vision_engine.get_desktop_context()
    assert isinstance(ctx, dict)
    assert "active_window" in ctx
    assert "active_process" in ctx


def test_vision_engine_analyze_with_ai(sample_image_base64):
    """Test 3: Verify multimodal vision reasoning generates comprehensive structured analysis."""
    analysis_res = vision_engine.analyze_image_with_ai(
        base64_data=sample_image_base64,
        goal="Diagnose the screen and explain what application is visible."
    )
    assert analysis_res["success"] is True
    assert "analysis" in analysis_res
    assert len(analysis_res["analysis"]) > 50
    assert "640" in analysis_res["analysis"]
    assert "480" in analysis_res["analysis"]


@pytest.mark.asyncio
async def test_agent_run_with_pasted_image(sample_image_base64):
    """Test 4: Verify HelperAgent run loop ingests image_data and returns immediate vision reply."""
    llm = LLMClient(provider="gemini")
    agent = HelperAgent(llm_client=llm, safe_mode=False, max_steps=5)

    emitted_events = []

    async def on_event(ev_type, data):
        emitted_events.append((ev_type, data))

    res = await agent.run(
        goal="Analyze this pasted screenshot and diagnose any errors.",
        on_event=on_event,
        image_data=sample_image_base64
    )

    assert res["success"] is True
    assert "message" in res
    assert len(res["message"]) > 0

    event_types = [e[0] for e in emitted_events]
    assert "image_analyzed" in event_types
    assert "completed" in event_types


def test_api_vision_analyze_endpoint(client, sample_image_base64):
    """Test 5: Verify FastAPI /api/vision/analyze direct endpoint."""
    resp = client.post(
        "/api/vision/analyze",
        json={"image_data": sample_image_base64, "prompt": "Check resolution and UI theme"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "analysis" in data
    assert data["metadata"]["width"] == 640


def test_api_execute_with_image_data(client, sample_image_base64):
    """Test 6: Verify FastAPI /api/run accepts goal with image_data."""
    resp = client.post(
        "/api/run",
        json={
            "goal": "Analyze this screenshot",
            "image_data": sample_image_base64
        }
    )
    assert resp.status_code in (200, 400)  # 200 if dispatched, 400 if already running
