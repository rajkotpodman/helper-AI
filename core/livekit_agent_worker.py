"""Helper-AI Official LiveKit Voice & Vision Agent Worker.

Runs an autonomous, sub-second WebRTC voice & multimodal vision assistant:
1. Real-time bi-directional conversation with barge-in / interruption handling.
2. WebRTC Video track processing (live desktop screen share or camera stream).
3. Helper-AI Tool Execution: Invokes PC diagnostics, PowerShell, file operations,
   and browser automation dynamically during speech.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

logger = logging.getLogger("HelperVoiceAgent")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    RunContext,
    cli,
    inference,
    TurnHandlingOptions
)
from livekit.agents.llm import function_tool

from core.livekit_bridge import livekit_bridge
from core.tools import ToolRegistry

registry = ToolRegistry()


class HelperVoiceAgent(Agent):
    """Voice & Vision persona for Helper-AI in LiveKit rooms."""

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are Helper-AI, an ultra-fast autonomous PC Control and Internet Agent. "
                "You interact with the user via real-time WebRTC voice and screen-sharing vision. "
                "Keep spoken responses concise, friendly, and natural. "
                "Do not use markdown, emojis, asterisks, or long tables in spoken speech. "
                "When asked to check PC health, run commands, inspect files, or automate websites, "
                "invoke the corresponding tool and summarize the result concisely."
            ),
        )

    async def on_enter(self) -> None:
        # Greet user upon entering room
        if hasattr(self, "session") and self.session:
            self.session.generate_reply(instructions="Greet the user warmly as Helper-AI and ask how you can assist their PC or research today.")

    @function_tool
    async def get_system_health(self, context: RunContext) -> str:
        """Checks local PC system health, CPU percentage, RAM memory usage, and free disk space."""
        res = await livekit_bridge.execute_tool_from_voice("get_system_health", {})
        return res.get("voice_narration", "Checked PC health successfully.")

    @function_tool
    async def run_powershell(self, context: RunContext, command: str) -> str:
        """Executes a Windows PowerShell terminal command on the local machine and returns output.
        
        Args:
            command: The PowerShell command string to execute (e.g. 'Get-Process | select -first 5').
        """
        res = await livekit_bridge.execute_tool_from_voice("run_powershell", {"command": command})
        return res.get("voice_narration", "Command executed.")

    @function_tool
    async def web_search(self, context: RunContext, query: str) -> str:
        """Searches the internet for real-time information, news, or articles.
        
        Args:
            query: The search keywords or question.
        """
        res = await livekit_bridge.execute_tool_from_voice("web_search", {"query": query})
        return res.get("voice_narration", "Web search completed.")

    @function_tool
    async def list_directory(self, context: RunContext, directory_path: str = ".") -> str:
        """Lists files and folders inside a given directory path on the local PC.
        
        Args:
            directory_path: Directory to inspect (defaults to current project).
        """
        res = await livekit_bridge.execute_tool_from_voice("list_directory", {"directory_path": directory_path})
        return res.get("voice_narration", "Directory listed.")

    @function_tool
    async def take_screenshot(self, context: RunContext) -> str:
        """Takes a desktop screenshot of the current screen."""
        res = await livekit_bridge.execute_tool_from_voice("take_screenshot", {})
        return res.get("voice_narration", "Screenshot captured.")


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """LiveKit WebRTC session handler."""
    logger.info(f"Starting Helper-AI Voice & Vision session in room: {ctx.room.name}")
    livekit_bridge.start_session(room_name=ctx.room.name)

    # Configure voice pipeline models
    stt_model = os.getenv("LIVEKIT_STT_MODEL", "deepgram/nova-3")
    llm_model = os.getenv("LIVEKIT_LLM_MODEL", "openai/gpt-4.1-mini")
    tts_model = os.getenv("LIVEKIT_TTS_MODEL", "cartesia/sonic-3")

    session = AgentSession(
        stt=inference.STT(stt_model, language="multi"),
        llm=inference.LLM(llm_model),
        tts=inference.TTS(tts_model),
        turn_handling=TurnHandlingOptions(
            interruption=True
        ),
    )

    agent = HelperVoiceAgent()
    await session.start(agent=agent, room=ctx.room)

    async def on_shutdown():
        livekit_bridge.stop_session()
        logger.info(f"Session closed for room: {ctx.room.name}")

    ctx.add_shutdown_callback(on_shutdown)


if __name__ == "__main__":
    cli.run_app(server)
