"""Voice speech tool for Helper-AI.

Allows the agent to speak messages aloud to the user using Edge-TTS neural speech synthesis.
"""
from typing import Dict, Any, Optional
from core.tools.base import BaseTool
from core.voice_engine import VoiceEngine, DEFAULT_VOICE


class VoiceSpeechTool(BaseTool):
    """Speaks aloud a message to the user through their PC speakers."""
    name = "speak_aloud"
    description = (
        "Speaks aloud a spoken message or goal completion notification to the user through their PC speakers "
        "using high-definition Microsoft Edge neural text-to-speech. Zero API key required."
    )
    parameters = {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The message to speak aloud clearly to the user."
            },
            "voice": {
                "type": "string",
                "description": "Optional neural voice name (e.g. 'en-US-AriaNeural', 'en-US-GuyNeural', 'hi-IN-SwaraNeural'). Default: en-US-AriaNeural.",
                "default": DEFAULT_VOICE
            }
        },
        "required": ["text"]
    }

    def execute(self, text: str, voice: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        target_voice = voice or DEFAULT_VOICE
        try:
            # Trigger audio playback
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(VoiceEngine.speak_on_pc(text, target_voice))
                else:
                    loop.run_until_complete(VoiceEngine.speak_on_pc(text, target_voice))
            except Exception:
                import threading
                threading.Thread(target=lambda: asyncio.run(VoiceEngine.speak_on_pc(text, target_voice)), daemon=True).start()

            return {
                "success": True,
                "output": f"Spoke aloud to user: '{text}' (Voice: {target_voice})",
                "text": text,
                "voice": target_voice
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"Failed to speak message: {str(e)}",
                "error": str(e)
            }
