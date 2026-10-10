"""Edge-TTS Voice Engine for Helper-AI.

Provides high-definition natural neural voice speech synthesis without requiring an API key.
Supports both local PC speaker playback and web audio streaming.
"""
import os
import asyncio
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, List, Dict

import edge_tts

logger = logging.getLogger("VoiceEngine")

DEFAULT_VOICE = "en-US-AriaNeural"
AVAILABLE_VOICES = [
    {"id": "en-US-AriaNeural", "name": "Aria (US Female - Crisp & Professional)"},
    {"id": "en-US-GuyNeural", "name": "Guy (US Male - Natural & Casual)"},
    {"id": "en-US-JennyNeural", "name": "Jenny (US Female - Warm & Conversational)"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia (UK Female - Clear & Formal)"},
    {"id": "hi-IN-SwaraNeural", "name": "Swara (Hindi/English Female - Bilingual)"},
    {"id": "hi-IN-MadhurNeural", "name": "Madhur (Hindi/English Male - Bilingual)"}
]


class VoiceEngine:
    """Manages Edge-TTS voice synthesis and playback."""

    @staticmethod
    async def synthesize_to_bytes(text: str, voice: str = DEFAULT_VOICE) -> bytes:
        """Synthesizes text to MP3 audio bytes asynchronously."""
        if not text or not text.strip():
            return b""
        
        communicate = edge_tts.Communicate(text.strip(), voice=voice)
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        return b"".join(audio_chunks)

    @classmethod
    def synthesize_bytes_sync(cls, text: str, voice: str = DEFAULT_VOICE) -> bytes:
        """Synchronous wrapper for synthesize_to_bytes."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In running loop (e.g. FastAPI), run in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(lambda: asyncio.run(cls.synthesize_to_bytes(text, voice))).result()
            else:
                return loop.run_until_complete(cls.synthesize_to_bytes(text, voice))
        except Exception:
            return asyncio.run(cls.synthesize_to_bytes(text, voice))

    @classmethod
    async def speak_on_pc(cls, text: str, voice: str = DEFAULT_VOICE) -> bool:
        """Synthesizes and plays audio directly out of the PC speakers on Windows."""
        try:
            audio_data = await cls.synthesize_to_bytes(text, voice)
            if not audio_data:
                return False

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
                tf.write(audio_data)
                temp_audio_path = tf.name

            # Play using PowerShell Windows Media Player component
            ps_script = f"""
            Add-Type -AssemblyName presentationCore
            $player = New-Object System.Windows.Media.MediaPlayer
            $player.Open([System.Uri]'{Path(temp_audio_path).as_uri()}')
            $player.Play()
            Start-Sleep -Milliseconds 1500
            while ($player.Position -lt $player.NaturalDuration.TimeSpan) {{
                Start-Sleep -Milliseconds 250
            }}
            $player.Close()
            """
            
            subprocess.Popen(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except Exception as e:
            logger.error(f"Failed to play speech on PC: {e}")
            return False

    @staticmethod
    def list_voices() -> List[Dict[str, str]]:
        """Returns popular voices supported out of the box."""
        return AVAILABLE_VOICES
