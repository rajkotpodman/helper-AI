"""Comprehensive Automated Test Suite for Helper-AI Hands-Free Voice Agent & Desktop Sidecar.

Tests:
1. VoiceEngine listing voices and metadata
2. Neural speech synthesis to audio bytes
3. FastAPI endpoints:
   - GET /api/voice/voices
   - POST /api/voice/synthesize
   - POST /api/voice/dispatch (system health, time, and conversational queries)
4. Desktop Voice Sidecar initialization and dispatch integration
"""

import os
import sys
import pytest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from app import app
from core.voice_engine import VoiceEngine, AVAILABLE_VOICES, DEFAULT_VOICE
from sidecar import DesktopVoiceSidecar


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_voice_engine_list_voices():
    """Test 1: Verify VoiceEngine returns curated list of neural voices."""
    voices = VoiceEngine.list_voices()
    assert isinstance(voices, list)
    assert len(voices) >= 6
    voice_ids = [v["id"] for v in voices]
    assert "en-US-AriaNeural" in voice_ids
    assert "gu-IN-DhwaniNeural" in voice_ids
    assert "hi-IN-SwaraNeural" in voice_ids


@pytest.mark.asyncio
async def test_voice_engine_synthesize_to_bytes():
    """Test 2: Verify neural audio synthesis produces MP3 audio bytes."""
    test_phrase = "Testing Helper-AI speech synthesis."
    audio_data = await VoiceEngine.synthesize_to_bytes(test_phrase, voice=DEFAULT_VOICE)
    assert audio_data is not None
    assert len(audio_data) > 500


def test_api_list_voices(client):
    """Test 3: Verify GET /api/voice/voices returns JSON list of voices."""
    resp = client.get("/api/voice/voices")
    assert resp.status_code == 200
    data = resp.json()
    assert "voices" in data
    assert len(data["voices"]) >= 6


def test_api_synthesize_voice(client):
    """Test 4: Verify POST /api/voice/synthesize streams valid audio/mpeg."""
    resp = client.post("/api/voice/synthesize", json={
        "text": "Hello, this is a test from Helper-AI.",
        "voice": DEFAULT_VOICE
    })
    assert resp.status_code == 200
    assert resp.headers.get("content-type") == "audio/mpeg"
    assert len(resp.content) > 500


def test_api_voice_dispatch_system_health(client):
    """Test 5: Verify POST /api/voice/dispatch handles fast system queries."""
    resp = client.post("/api/voice/dispatch", json={
        "transcript": "What is my CPU and RAM usage?",
        "voice": DEFAULT_VOICE,
        "speak_on_pc": False
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["tool_executed"] == "get_system_health"
    assert "CPU" in data["reply"]
    assert "audio_base64" in data
    assert len(data["audio_base64"]) > 100


def test_api_voice_dispatch_time(client):
    """Test 6: Verify POST /api/voice/dispatch handles time query."""
    resp = client.post("/api/voice/dispatch", json={
        "transcript": "Tell me what time it is.",
        "voice": DEFAULT_VOICE,
        "speak_on_pc": False
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "time" in data["reply"].lower()
    assert len(data["audio_base64"]) > 50


def test_desktop_sidecar_initialization():
    """Test 7: Verify DesktopVoiceSidecar initializes with proper defaults."""
    sidecar = DesktopVoiceSidecar(server_url="http://127.0.0.1:8000", voice="en-US-AriaNeural")
    assert sidecar.server_url == "http://127.0.0.1:8000"
    assert sidecar.voice == "en-US-AriaNeural"
    assert sidecar._user32 is not None
