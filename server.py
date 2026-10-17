"""Helper-AI: High-Speed FastAPI Backend Server & UI Host.

Production-grade, asynchronous backend serving the glassmorphic cyber dark-mode
Helper-AI web interface, live telemetry, WebSocket execution pipeline, and agent tools.
"""
import os
import sys
import json
import asyncio
import logging
import platform
import webbrowser
from pathlib import Path
from typing import Dict, Any, List, Optional

import psutil
from dotenv import load_dotenv, set_key
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load environment configuration
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("HelperServer")

# Core agent imports
from core.agent import HelperAgent
from core.llm import LLMClient
from core.tools import ToolRegistry
from core.metrics import metrics
from core.audit import audit_logger
from core.permissions import PermissionManager
from core.memory_recorder import MarkdownMemoryRecorder
from core.translator import translator

# Initialize FastAPI app
app = FastAPI(
    title="Helper-AI • Autonomous PC & Internet Agent",
    description="Production-grade autonomous agent backend with real-time telemetry and cyber UI",
    version="2.0.0"
)

# CORS middleware for local or cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Mount Static Assets & Screenshots
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/screenshots", StaticFiles(directory=str(SCREENSHOTS_DIR)), name="screenshots")

# Global State Management
permission_manager = PermissionManager()
memory_recorder = MarkdownMemoryRecorder()
active_agent: Optional[HelperAgent] = None
active_task: Optional[asyncio.Task] = None
connected_websockets: List[WebSocket] = []

current_goal_info = {
    "is_running": False,
    "goal": "",
    "history": [],
    "last_result": None
}


# Pydantic Request Models
class GoalExecutionRequest(BaseModel):
    goal: str = Field(..., description="The user's automation prompt or goal")
    provider: Optional[str] = Field("gemini", description="LLM provider: gemini, openai, groq, ollama, rule_engine")
    engine: Optional[str] = Field("native", description="Automation engine")
    safe_mode: Optional[bool] = Field(False, description="Whether to require confirmation before sensitive actions")
    max_steps: Optional[int] = Field(50, description="Maximum autonomous loops")
    language: Optional[str] = Field("en", description="Target response language code")


class ApprovePermissionRequest(BaseModel):
    request_id: Optional[str] = None
    approved: bool = True


class SettingsUpdateRequest(BaseModel):
    provider: Optional[str] = "gemini"
    gemini_key: Optional[str] = None
    openai_key: Optional[str] = None
    groq_key: Optional[str] = None
    deepseek_key: Optional[str] = None
    custom_name: Optional[str] = None
    custom_url: Optional[str] = None
    custom_key: Optional[str] = None
    custom_model: Optional[str] = None
    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None
    safe_mode: Optional[bool] = False


class TranslationApiRequest(BaseModel):
    text: Optional[str] = ""
    texts: Optional[List[str]] = None
    target_lang: str = "en"
    source_lang: Optional[str] = "auto"


# --- Real-Time WebSocket Broadcaster ---
async def broadcast_ws(event_type: str, data: Dict[str, Any]):
    """Broadcast real-time JSON events to all active WebSocket clients."""
    payload = json.dumps({"type": event_type, "event": event_type, **data})
    disconnected = []
    for ws in connected_websockets:
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        if ws in connected_websockets:
            connected_websockets.remove(ws)


def _on_permission_notify(req_data: dict):
    """Callback for human-in-the-loop authorization requests."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(broadcast_ws("permission_requested", req_data))
    except Exception as e:
        logger.warning(f"Failed to push permission notification: {e}")


permission_manager.set_listener(_on_permission_notify)


# --- Root Route: Serve Modern Glassmorphic Cyber UI ---
@app.get("/")
async def serve_index_page():
    """Serves the primary Helper-AI single-page application."""
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse(status_code=404, content={"error": "index.html template not found in web/templates"})


# --- WebSocket Endpoint for Telemetry Stream ---
@app.websocket("/ws")
async def websocket_telemetry(websocket: WebSocket):
    """Real-time bi-directional streaming endpoint for step progress and logs."""
    await websocket.accept()
    connected_websockets.append(websocket)
    try:
        # Initial greeting with system state
        await websocket.send_text(json.dumps({
            "type": "init",
            "event": "init",
            "is_running": current_goal_info["is_running"],
            "current_goal": current_goal_info["goal"],
            "history_count": len(current_goal_info["history"])
        }))
        while True:
            msg = await websocket.receive_text()
            try:
                msg_data = json.loads(msg)
                if msg_data.get("type") == "ping":
                    import time
                    await websocket.send_text(json.dumps({"type": "pong", "timestamp": time.time()}))
            except Exception:
                pass
    except WebSocketDisconnect:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)


# --- Required Specification Endpoint: POST /api/execute ---
@app.post("/api/execute")
@app.post("/api/run")
async def execute_agent_goal(req: GoalExecutionRequest):
    """Execute an autonomous automation goal pipeline and return result status."""
    global active_agent, active_task, current_goal_info

    goal_str = req.goal.strip()
    if not goal_str:
        raise HTTPException(status_code=400, detail="Goal prompt cannot be empty.")

    if current_goal_info["is_running"]:
        raise HTTPException(status_code=409, detail="An autonomous goal is already running. Please wait or stop it.")

    # Determine loop limits
    max_steps = req.max_steps or 50
    is_heavy = any(k in goal_str.lower() for k in ["/goal", "heavy", "long", "deep", "full web", "crawl", "build", "implement", "project", "all", "5 "])
    if is_heavy:
        max_steps = max(max_steps, 200)

    # Initialize LLM and Agent
    provider = req.provider or os.getenv("LLM_PROVIDER", "gemini")
    llm = LLMClient(provider=provider)
    active_agent = HelperAgent(
        llm_client=llm,
        safe_mode=bool(req.safe_mode),
        max_steps=max_steps,
        permission_manager=permission_manager,
        memory_recorder=memory_recorder
    )

    current_goal_info["is_running"] = True
    current_goal_info["goal"] = goal_str
    current_goal_info["history"] = []
    current_goal_info["last_result"] = None

    await broadcast_ws("started", {
        "goal": goal_str,
        "provider": provider,
        "safe_mode": req.safe_mode,
        "max_steps": max_steps
    })

    async def execute_pipeline():
        global current_goal_info
        try:
            async def on_event_callback(event_type: str, data: dict):
                await broadcast_ws(event_type, data)
                if event_type in ("action_result", "thought", "step_start", "action"):
                    current_goal_info["history"].append({"type": event_type, **data})

            # Run autonomous agent loop
            result = await active_agent.run(goal_str, on_event=on_event_callback)
            current_goal_info["last_result"] = result
            await broadcast_ws("completed", result or {"success": True, "final_result": "Goal finished."})
            return result
        except asyncio.CancelledError:
            await broadcast_ws("cancelled", {"message": "Goal was stopped by user."})
        except Exception as ex:
            logger.error(f"Error during agent pipeline: {ex}", exc_info=True)
            await broadcast_ws("error", {"message": str(ex)})
        finally:
            current_goal_info["is_running"] = False

    active_task = asyncio.create_task(execute_pipeline())
    
    # If the client is expecting an immediate synchronous result from /api/execute, wait briefly or return initiated status
    try:
        # Give fast tasks up to 1.5 seconds to return immediate response or return dispatch acknowledgment
        done, _ = await asyncio.wait([active_task], timeout=1.5)
        if active_task in done:
            res = active_task.result()
            return JSONResponse(content={
                "success": True,
                "status": "completed",
                "goal": goal_str,
                "final_result": res.get("final_result", "Goal completed."),
                "history": current_goal_info["history"]
            })
    except Exception:
        pass

    return {
        "success": True,
        "status": "initiated",
        "goal": goal_str,
        "provider": provider,
        "message": "Autonomous goal pipeline started. Follow progress on WebSocket or execution drawer."
    }


# --- Required Specification Endpoint: GET /api/system-status ---
@app.get("/api/system-status")
async def get_system_status():
    """Returns live CPU, RAM, OS, and memory telemetry."""
    try:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage(str(Path.cwd().anchor))
    except Exception:
        cpu = 0.0
        mem = type("Obj", (), {"percent": 0.0, "used": 0, "total": 0})()
        disk = type("Obj", (), {"percent": 0.0, "free": 0})()

    tools = ToolRegistry()
    return {
        "status": "online",
        "is_running": current_goal_info["is_running"],
        "cpu_percent": round(cpu, 1),
        "ram_percent": round(mem.percent, 1),
        "ram_used_gb": round(getattr(mem, "used", 0) / (1024 ** 3), 2),
        "ram_total_gb": round(getattr(mem, "total", 0) / (1024 ** 3), 2),
        "disk_free_gb": round(getattr(disk, "free", 0) / (1024 ** 3), 1),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "tools_registered": len(tools.get_all_tools()),
        "memory_file_size_mb": memory_recorder.get_size_mb(),
        "memory_entries": memory_recorder.get_entry_count(),
        "provider": os.getenv("LLM_PROVIDER", "gemini"),
        "safe_mode": os.getenv("SAFE_MODE", "false").lower() == "true"
    }


@app.get("/api/tools")
async def get_tools():
    """Enumerates all registered tools with schemas."""
    tools = ToolRegistry()
    return {"tools": tools.get_schemas(), "count": len(tools.get_all_tools())}


# --- Connection Diagnostic Endpoints ---
@app.get("/api/connections/check")
@app.get("/api/check-connections")
async def check_all_connections(pass_count: int = 2):
    """Diagnoses and tests all connections (Internet, Google Translate, LLM APIs, Chrome CDP, MCP, WebSocket)."""
    from core.connection_checker import connection_checker
    if pass_count >= 2:
        return connection_checker.check_twice()
    return connection_checker.check_all()


# --- Required Specification Endpoint: GET /api/quick-ideas ---
@app.get("/api/quick-ideas")
async def get_quick_ideas():
    """Returns available quick idea templates for one-click prompts."""
    return {
        "ideas": [
            {
                "id": "check_connections",
                "icon": "⚡",
                "title": "Check Connections Twice",
                "prompt": "run check twice all connection fix with more faster accurate smart work",
                "category": "Diagnostics"
            },
            {
                "id": "google_blogs",
                "icon": "🌐",
                "title": "List My Google Blogs",
                "prompt": "give me the list of my google blogs",
                "category": "Web Automation"
            },
            {
                "id": "pc_health",
                "icon": "💻",
                "title": "PC Health Diagnostic",
                "prompt": "Check my PC health, CPU, RAM and disk usage",
                "category": "System Maintenance"
            },
            {
                "id": "ai_research",
                "icon": "🔍",
                "title": "Web Research Report",
                "prompt": "Search the web for top 5 AI agent frameworks and write summary to Desktop",
                "category": "Deep Research"
            },
            {
                "id": "clean_downloads",
                "icon": "📁",
                "title": "Inspect Downloads",
                "prompt": "List the largest files in my Downloads folder",
                "category": "File System"
            },
            {
                "id": "sysinfo_desktop",
                "icon": "📄",
                "title": "System Info to Desktop",
                "prompt": "Open PowerShell, test git version and write system info to Desktop/sysinfo.txt",
                "category": "Productivity"
            }
        ]
    }


# --- Memory Telemetry Endpoints ---
@app.get("/api/memory/stats")
@app.get("/api/memory/status")
async def get_memory_stats():
    """Returns memory file telemetry (agent_memory.md)."""
    return {
        "file_name": memory_recorder.file_path.name,
        "file_path": str(memory_recorder.file_path),
        "size_bytes": memory_recorder.get_size_bytes(),
        "size_mb": memory_recorder.get_size_mb(),
        "limit_mb": 20.0,
        "prompt_count": memory_recorder.get_entry_count(),
        "is_limit_reached": memory_recorder.is_limit_reached()
    }


@app.get("/api/memory/download")
async def download_memory_file():
    """Allows downloading the persistent agent_memory.md directly."""
    if not memory_recorder.file_path.exists():
        memory_recorder._init_file()
    return FileResponse(
        path=str(memory_recorder.file_path),
        filename=memory_recorder.file_path.name,
        media_type="text/markdown"
    )


@app.post("/api/memory/reset")
async def reset_memory_file():
    """Resets agent_memory.md back to 0 bytes with clean headers."""
    memory_recorder.reset_file()
    await broadcast_ws("memory_reset", {"message": "Memory log file has been reset."})
    return {"success": True, "message": "Memory log cleared successfully."}


# --- Agent Cancellation ---
@app.post("/api/cancel")
async def cancel_running_agent():
    """Immediately halts any running autonomous agent task."""
    global active_agent, active_task, current_goal_info
    permission_manager.cancel_all()
    if active_agent and current_goal_info["is_running"]:
        active_agent.cancel()
    if active_task and not active_task.done():
        active_task.cancel()
    current_goal_info["is_running"] = False
    await broadcast_ws("cancelled", {"message": "User stopped execution."})
    return {"success": True, "message": "Agent execution halted."}


# --- Settings Configuration API ---
@app.post("/api/settings")
async def update_settings(req: SettingsUpdateRequest):
    """Updates API keys and system settings in the .env file."""
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        env_file.touch()

    if req.provider:
        os.environ["LLM_PROVIDER"] = req.provider
        set_key(str(env_file), "LLM_PROVIDER", req.provider)
    if req.gemini_key is not None:
        os.environ["GEMINI_API_KEY"] = req.gemini_key
        set_key(str(env_file), "GEMINI_API_KEY", req.gemini_key)
    if req.openai_key is not None:
        os.environ["OPENAI_API_KEY"] = req.openai_key
        set_key(str(env_file), "OPENAI_API_KEY", req.openai_key)
    if req.groq_key is not None:
        os.environ["GROQ_API_KEY"] = req.groq_key
        set_key(str(env_file), "GROQ_API_KEY", req.groq_key)
    if req.deepseek_key is not None:
        os.environ["DEEPSEEK_API_KEY"] = req.deepseek_key
        set_key(str(env_file), "DEEPSEEK_API_KEY", req.deepseek_key)
    if req.custom_name is not None:
        os.environ["CUSTOM_LLM_NAME"] = req.custom_name
        set_key(str(env_file), "CUSTOM_LLM_NAME", req.custom_name)
    if req.custom_url is not None:
        os.environ["CUSTOM_LLM_URL"] = req.custom_url
        set_key(str(env_file), "CUSTOM_LLM_URL", req.custom_url)
    if req.custom_key is not None:
        os.environ["CUSTOM_LLM_KEY"] = req.custom_key
        set_key(str(env_file), "CUSTOM_LLM_KEY", req.custom_key)
    if req.custom_model is not None:
        os.environ["CUSTOM_LLM_MODEL"] = req.custom_model
        set_key(str(env_file), "CUSTOM_LLM_MODEL", req.custom_model)
    if req.ollama_url:
        os.environ["OLLAMA_BASE_URL"] = req.ollama_url
        set_key(str(env_file), "OLLAMA_BASE_URL", req.ollama_url)
    if req.ollama_model:
        os.environ["OLLAMA_MODEL"] = req.ollama_model
        set_key(str(env_file), "OLLAMA_MODEL", req.ollama_model)
    if req.safe_mode is not None:
        os.environ["SAFE_MODE"] = str(req.safe_mode).lower()
        set_key(str(env_file), "SAFE_MODE", str(req.safe_mode).lower())

    return {"success": True, "message": "Settings updated successfully."}


# --- Project Browser Launcher ---
@app.post("/api/browser/launch")
async def launch_project_browser():
    """Opens dedicated Project Chrome Browser session on the desktop."""
    try:
        from core.browser_driver import ProjectBrowser
        browser = ProjectBrowser.get_instance()
        browser.navigate("https://www.blogger.com")
        browser.bring_to_front()
        return {
            "success": True,
            "message": "Project Chrome Browser opened on screen. You can log into your account directly."
        }
    except Exception as e:
        logger.error(f"Failed to launch project browser: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# --- Human-in-the-Loop Approval Endpoints ---
@app.post("/api/approve")
@app.post("/api/permission/respond")
async def approve_pending_action(req: ApprovePermissionRequest):
    """1-Click human authorization to approve or deny sensitive agent actions."""
    req_id = req.request_id or permission_manager.get_first_pending_id()
    if req_id:
        success = permission_manager.respond(req_id, req.approved)
        await broadcast_ws("permission_decided", {
            "request_id": req_id,
            "approved": req.approved,
            "success": success
        })
        return {"success": success, "approved": req.approved}
    return {"success": False, "message": "No pending authorization request found."}


# --- Translation Services ---
@app.get("/api/translate/languages")
async def list_translate_languages():
    """List Google Translate supported languages."""
    return {"languages": translator.get_supported_languages()}


@app.post("/api/translate")
async def translate_text(req: TranslationApiRequest):
    """Universal machine translation endpoint."""
    if req.texts:
        translated = translator.batch_translate(req.texts, target_lang=req.target_lang, source_lang=req.source_lang or "auto")
        return {"translated_texts": translated, "target_lang": req.target_lang}
    translated = translator.translate_text(req.text or "", target_lang=req.target_lang, source_lang=req.source_lang or "auto")
    return {"translated_text": translated, "target_lang": req.target_lang}


# --- Edge-TTS Voice Output ---
@app.post("/api/voice/speak")
async def speak_text_on_pc(payload: Dict[str, Any]):
    """Read aloud text using Edge-TTS or system speech."""
    from core.voice_engine import VoiceEngine, DEFAULT_VOICE
    text = payload.get("text", "")
    voice = payload.get("voice", DEFAULT_VOICE)
    if not text:
        return JSONResponse(status_code=400, content={"error": "Text is required"})
    res = await VoiceEngine.speak_on_pc(text, voice)
    return {"success": res, "text": text, "voice": voice}


# --- Execution Launcher Helper ---
def start_server(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = False):
    """Launch the FastAPI server using Uvicorn."""
    import uvicorn
    if open_browser:
        import threading
        import time
        threading.Timer(1.2, lambda: webbrowser.open(f"http://{host}:{port}")).start()
    uvicorn.run("server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    logger.info(f"Starting Helper-AI Cyber Server on http://{host}:{port}")
    start_server(host=host, port=port, open_browser=False)
