"""Edge-TTS Voice Engine for Helper-AI.

Provides high-definition natural neural voice speech synthesis with zero-key cloud
Edge-TTS and automatic offline SAPI5 fallback. Supports both local PC speaker playback
and high-speed Web Audio streaming.
"""
import os
import asyncio
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

import edge_tts

logger = logging.getLogger("VoiceEngine")

DEFAULT_VOICE = "en-US-AriaNeural"
AVAILABLE_VOICES = [
    {"id": "en-US-AriaNeural", "name": "Aria (US Female - Crisp & Professional)", "lang": "en-US", "gender": "Female"},
    {"id": "en-US-GuyNeural", "name": "Guy (US Male - Natural & Casual)", "lang": "en-US", "gender": "Male"},
    {"id": "en-US-JennyNeural", "name": "Jenny (US Female - Warm & Conversational)", "lang": "en-US", "gender": "Female"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia (UK Female - Clear & Formal)", "lang": "en-GB", "gender": "Female"},
    {"id": "hi-IN-SwaraNeural", "name": "Swara (Hindi/English Female - Bilingual)", "lang": "hi-IN", "gender": "Female"},
    {"id": "hi-IN-MadhurNeural", "name": "Madhur (Hindi/English Male - Bilingual)", "lang": "hi-IN", "gender": "Male"},
    {"id": "gu-IN-DhwaniNeural", "name": "Dhwani (Gujarati Female - Natural)", "lang": "gu-IN", "gender": "Female"},
    {"id": "gu-IN-NiranjanNeural", "name": "Niranjan (Gujarati Male - Clear)", "lang": "gu-IN", "gender": "Male"}
]


class VoiceEngine:
    """Manages Edge-TTS voice synthesis, fallback SAPI5 playback, and audio streaming."""

    @staticmethod
    async def synthesize_to_bytes(
        text: str,
        voice: str = DEFAULT_VOICE,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%"
    ) -> bytes:
        """Synthesizes text to MP3 audio bytes asynchronously with offline fallback."""
        cleaned_text = (text or "").strip()
        if not cleaned_text:
            return b""
        
        # 1. Try High-Quality Neural Edge-TTS
        try:
            communicate = edge_tts.Communicate(
                cleaned_text,
                voice=voice,
                rate=rate,
                pitch=pitch,
                volume=volume
            )
            audio_chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])
            
            if audio_chunks:
                return b"".join(audio_chunks)
        except Exception as e:
            logger.warning(f"Edge-TTS synthesis error ({e}). Attempting local fallback.")

        # 2. Local Fallback via Windows PowerShell SpeechSynthesizer if offline
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                temp_wav = tf.name
            
            escaped_text = cleaned_text.replace("'", "''").replace('"', '`"')
            ps_script = f"""
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.SetOutputToWaveFile('{temp_wav}')
            $synth.Speak('{escaped_text}')
            $synth.Dispose()
            """
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10
            )
            if proc.returncode == 0 and os.path.exists(temp_wav):
                with open(temp_wav, "rb") as f:
                    data = f.read()
                try:
                    os.remove(temp_wav)
                except Exception:
                    pass
                return data
        except Exception as fb_err:
            logger.error(f"Local speech synthesis fallback failed: {fb_err}")

        return b""

    @classmethod
    def synthesize_bytes_sync(cls, text: str, voice: str = DEFAULT_VOICE) -> bytes:
        """Synchronous wrapper for synthesize_to_bytes."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
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
            Start-Sleep -Milliseconds 1200
            $timeout = 0
            while ($player.Position -lt $player.NaturalDuration.TimeSpan -and $timeout -lt 60) {{
                Start-Sleep -Milliseconds 200
                $timeout += 0.2
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
