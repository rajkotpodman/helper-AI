"""Comprehensive Automated Verification Test Suite for LiveKit Integration with Helper-AI.

Tests:
1. LiveKit library and plugin presence
2. LiveKitBridge initialization & status inspection
3. WebRTC JWT Token Generation (room & identity grants)
4. Helper-AI ToolRegistry bridging (37+ tools exposed for voice/multimodal)
5. Live Voice Tool Execution & Speech Narration generation
6. Live Session Lifecycle & Transcript Memory
7. ConnectionChecker double-pass diagnostics inclusion
8. FastAPI LiveKit endpoints via TestClient (/api/livekit/status, /api/livekit/token, etc.)
"""

import sys
import pytest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from app import app
from core.livekit_bridge import LiveKitBridge, livekit_bridge
from core.connection_checker import ConnectionChecker


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_livekit_packages_installed():
    """Test 1: Verify LiveKit core, agents, and plugins are installed."""
    import livekit
    import livekit.api
    import livekit.agents
    from importlib.metadata import version
    assert version("livekit") is not None
    assert livekit.agents.__version__ is not None


def test_livekit_bridge_singleton_and_tools_count():
    """Test 2: Verify LiveKitBridge singleton and bridged tools count."""
    bridge = LiveKitBridge.get_instance()
    status = bridge.get_status()
    assert status["available"] is True
    assert status["tools_bridged_count"] >= 30
    assert status["default_room"] == "helper-ai-room"


def test_livekit_token_generation():
    """Test 3: Verify WebRTC JWT Token generation with video/audio grants."""
    token_res = livekit_bridge.generate_token(room_name="test-voice-room", identity="test_user_42", name="Tester")
    assert token_res["success"] is True
    assert token_res["token"] is not None
    assert len(token_res["token"]) > 100
    assert token_res["room"] == "test-voice-room"
    assert token_res["identity"] == "test_user_42"


def test_livekit_connection_diagnostic():
    """Test 4: Verify LiveKit connection diagnostic health check."""
    diag = livekit_bridge.test_connection()
    assert diag["name"] == "livekit_webrtc"
    assert diag["status"] in ("connected", "standby_ready")
    assert diag["tools_bridged"] >= 30


@pytest.mark.asyncio
async def test_livekit_voice_tool_execution():
    """Test 5: Verify voice tool execution produces concise narration."""
    res = await livekit_bridge.execute_tool_from_voice("get_system_health", {})
    assert res["success"] is True
    assert res["tool"] == "get_system_health"
    assert "voice_narration" in res
    assert len(res["voice_narration"]) > 0


def test_livekit_session_lifecycle_and_transcripts():
    """Test 6: Verify session start, transcript logging, and stop."""
    start_res = livekit_bridge.start_session("unit-test-room")
    assert start_res["success"] is True
    assert start_res["active"] is True
    assert start_res["room"] == "unit-test-room"

    livekit_bridge.record_transcript("User", "Check CPU usage")
    livekit_bridge.record_transcript("Helper-AI", "CPU usage is 12 percent")

    transcripts = livekit_bridge.get_recent_transcripts(limit=5)
    assert len(transcripts) >= 2
    assert transcripts[-1]["speaker"] == "Helper-AI"
    assert "CPU usage is 12 percent" in transcripts[-1]["text"]

    stop_res = livekit_bridge.stop_session()
    assert stop_res["success"] is True
    assert stop_res["active"] is False


def test_connection_checker_includes_livekit():
    """Test 7: Verify ConnectionChecker includes livekit_webrtc in double-pass audit."""
    cc = ConnectionChecker.get_instance()
    res = cc.check_all(timeout=2.0)
    assert "connections" in res
    assert "livekit_webrtc" in res["connections"]
    lk_check = res["connections"]["livekit_webrtc"]
    assert lk_check["status"] in ("connected", "standby_ready")


def test_fastapi_livekit_api_routes(client):
    """Test 8: Verify all FastAPI LiveKit endpoints function correctly."""
    # GET status
    status_resp = client.get("/api/livekit/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["available"] is True

    # POST token
    tok_resp = client.post("/api/livekit/token", json={"room": "api-test-room", "identity": "tester"})
    assert tok_resp.status_code == 200
    tok_data = tok_resp.json()
    assert tok_data["success"] is True
    assert "token" in tok_data

    # POST session start & stop
    start_resp = client.post("/api/livekit/session/start", json={"room": "api-test-room"})
    assert start_resp.status_code == 200
    assert start_resp.json()["active"] is True

    stop_resp = client.post("/api/livekit/session/stop")
    assert stop_resp.status_code == 200
    assert stop_resp.json()["active"] is False

    # POST execute tool from voice
    tool_resp = client.post("/api/livekit/execute-tool", json={"tool": "get_system_health", "arguments": {}})
    assert tool_resp.status_code == 200
    tool_data = tool_resp.json()
    assert tool_data["success"] is True
    assert "voice_narration" in tool_data
