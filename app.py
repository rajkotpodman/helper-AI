"""Helper-AI: Web Dashboard and API Server."""
import os
import sys
import json
import asyncio
import webbrowser
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv, set_key
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

load_dotenv()

from core.agent import HelperAgent
from core.llm import LLMClient
from core.tools import ToolRegistry
from core.metrics import metrics
from core.audit import audit_logger
from core.permissions import PermissionManager
from core.memory_recorder import MarkdownMemoryRecorder

app = FastAPI(title="Helper-AI Dashboard")

# Global agent manager state
permission_manager = PermissionManager()
memory_recorder = MarkdownMemoryRecorder()
active_agent: HelperAgent = None
active_task: asyncio.Task = None
connected_websockets: list[WebSocket] = []
current_goal_info = {
    "is_running": False,
    "goal": "",
    "history": []
}

from typing import Optional

class GoalRequest(BaseModel):
    goal: str
    provider: Optional[str] = None
    engine: Optional[str] = "native"
    safe_mode: bool = False
    max_steps: int = 50

class PermissionRespondRequest(BaseModel):
    request_id: str
    approved: bool

class SettingsRequest(BaseModel):
    provider: str
    gemini_key: Optional[str] = None
    openai_key: Optional[str] = None
    groq_key: Optional[str] = None
    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None
    safe_mode: bool = False

async def broadcast_event(event_type: str, data: dict):
    message = json.dumps({"event": event_type, "data": data})
    disconnected = []
    for ws in connected_websockets:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        if ws in connected_websockets:
            connected_websockets.remove(ws)

def _notify_permission_req(req_data: dict):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(broadcast_event("permission_requested", req_data))
    except Exception:
        pass

permission_manager.set_listener(_notify_permission_req)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.append(websocket)
    # Send current state
    await websocket.send_text(json.dumps({
        "event": "init",
        "data": {
            "is_running": current_goal_info["is_running"],
            "current_goal": current_goal_info["goal"],
            "history_count": len(current_goal_info["history"])
        }
    }))
    try:
        while True:
            # Keep socket alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)

@app.get("/api/status")
async def get_status():
    tools = ToolRegistry()
    return {
        "is_running": current_goal_info["is_running"],
        "goal": current_goal_info["goal"],
        "tools_count": len(tools.get_all_tools()),
        "provider": os.getenv("LLM_PROVIDER", "gemini"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b"),
        "has_gemini_key": bool(os.getenv("GEMINI_API_KEY")),
        "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "has_groq_key": bool(os.getenv("GROQ_API_KEY"))
    }

@app.get("/api/ollama/models")
async def get_ollama_models():
    import requests
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        r = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=3)
        if r.status_code == 200:
            return {"models": [m.get("name") for m in r.json().get("models", [])]}
    except Exception:
        pass
    return {"models": []}

@app.get("/api/tools")
async def get_tools():
    tools = ToolRegistry()
    return {"tools": tools.get_schemas()}

@app.get("/api/metrics")
async def get_metrics():
    return metrics.get_snapshot()

@app.get("/api/audit")
async def get_audit(limit: int = 50):
    lines = []
    if audit_logger.audit_file.exists():
        with open(audit_logger.audit_file, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            for line in all_lines[-limit:]:
                try:
                    lines.append(json.loads(line.strip()))
                except Exception:
                    continue
    return {"events": lines, "total_logged": len(lines)}

@app.get("/api/export")
async def export_history(format: str = "json"):
    if format == "markdown":
        md = f"# Helper-AI Goal Execution Report\n\n**Goal:** {current_goal_info['goal']}\n\n"
        for idx, item in enumerate(current_goal_info["history"], start=1):
            md += f"### Step {idx} ({item.get('action', 'none')})\n"
            md += f"**Success:** {item.get('success')}\n\n```\n{item.get('output', '')}\n```\n\n"
        return JSONResponse(content={"markdown": md})
    return {"goal": current_goal_info["goal"], "history": current_goal_info["history"]}

@app.get("/api/permission/pending")
async def get_pending_permission():
    pending = permission_manager.get_pending()
    return {"pending": pending}

@app.post("/api/permission/respond")
async def respond_to_permission(req: PermissionRespondRequest):
    success = permission_manager.respond(req.request_id, req.approved)
    await broadcast_event("permission_decided", {
        "request_id": req.request_id,
        "approved": req.approved,
        "success": success
    })
    return {
        "success": success,
        "request_id": req.request_id,
        "approved": req.approved,
        "message": "Authorization recorded." if success else "Request not found or already closed."
    }

@app.get("/api/memory/status")
async def get_memory_status():
    return {
        "file_path": str(memory_recorder.file_path),
        "file_name": memory_recorder.file_path.name,
        "size_bytes": memory_recorder.get_size_bytes(),
        "size_mb": memory_recorder.get_size_mb(),
        "limit_mb": round(memory_recorder.max_bytes / (1024 * 1024), 1),
        "total_prompts": memory_recorder.get_entry_count(),
        "is_limit_reached": memory_recorder.is_limit_reached()
    }

@app.get("/api/memory/download")
async def download_memory_file():
    if not memory_recorder.file_path.exists():
        memory_recorder._init_file()
    return FileResponse(
        path=str(memory_recorder.file_path),
        filename=memory_recorder.file_path.name,
        media_type="text/markdown"
    )

@app.post("/api/memory/reset")
async def reset_memory_file():
    memory_recorder.reset_file()
    await broadcast_event("memory_reset", {"message": "Memory log file has been reset."})
    return {"success": True, "message": "Memory file has been reset to 0 bytes with a fresh header."}

@app.get("/api/engines")
async def get_available_engines():
    return {
        "status": "ready",
        "engine": "native",
        "description": "Helper-AI Autonomous PC Control & Internet Agent"
    }

@app.post("/api/run")
async def start_goal(req: GoalRequest):
    global active_agent, active_task, current_goal_info

    if current_goal_info["is_running"]:
        return JSONResponse(status_code=400, content={"error": "An agent task is already actively running."})

    goal_str = req.goal.strip()
    if not goal_str:
        return JSONResponse(status_code=400, content={"error": "Goal cannot be empty."})

    steps = req.max_steps
    if steps <= 25:
        steps = 50
    if "/goal" in goal_str.lower() or "5 " in goal_str.lower() or "apply" in goal_str.lower():
        steps = max(steps, 100)

    llm = LLMClient(provider=req.provider)
    active_agent = HelperAgent(
        llm_client=llm,
        safe_mode=req.safe_mode,
        max_steps=steps,
        permission_manager=permission_manager,
        memory_recorder=memory_recorder
    )

    current_goal_info["is_running"] = True
    current_goal_info["goal"] = goal_str
    current_goal_info["history"] = []

    async def run_worker():
        global active_agent, current_goal_info
        try:
            async def on_event(ev_type: str, data: dict):
                await broadcast_event(ev_type, data)
                if ev_type in ("action_result", "thought", "step_start"):
                    current_goal_info["history"].append(data)

            result = await active_agent.run(goal_str, on_event=on_event)
            await broadcast_event("finished", result or {"success": True, "message": "Goal finished."})
        except Exception as e:
            logger.error(f"Exception during agent run: {e}", exc_info=True)
            await broadcast_event("error", {"error": str(e)})
        finally:
            current_goal_info["is_running"] = False

    active_task = asyncio.create_task(run_worker())
    return {"success": True, "message": "Agent execution initiated."}


@app.post("/api/cancel")
async def cancel_goal():
    global active_agent, current_goal_info
    permission_manager.cancel_all()
    if active_agent and current_goal_info["is_running"]:
        active_agent.cancel()
        current_goal_info["is_running"] = False
        await broadcast_event("cancelled", {"message": "User stopped execution."})
        return {"success": True, "message": "Agent cancel signal sent."}
    return {"success": False, "message": "No active agent running."}

@app.post("/api/settings")
async def update_settings(req: SettingsRequest):
    env_file = Path.cwd() / ".env"
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
    if req.ollama_url:
        os.environ["OLLAMA_BASE_URL"] = req.ollama_url
        set_key(str(env_file), "OLLAMA_BASE_URL", req.ollama_url)
    if req.ollama_model:
        os.environ["OLLAMA_MODEL"] = req.ollama_model
        set_key(str(env_file), "OLLAMA_MODEL", req.ollama_model)

    os.environ["SAFE_MODE"] = str(req.safe_mode).lower()
    set_key(str(env_file), "SAFE_MODE", str(req.safe_mode).lower())

    return {"success": True, "message": "Settings updated successfully."}

@app.post("/api/browser/launch")
async def launch_project_browser():
    try:
        from core.browser_driver import ProjectBrowser
        browser = ProjectBrowser.get_instance()
        res = browser.navigate("https://www.blogger.com")
        browser.bring_to_front()
        return {
            "success": True,
            "message": "Project Chrome Browser is now open on your screen showing Blogger. You can sign into your Google account directly in that window."
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/voice/speak")
async def api_voice_speak(payload: Dict[str, Any]):
    from core.voice_engine import VoiceEngine, DEFAULT_VOICE
    text = payload.get("text", "")
    voice = payload.get("voice", DEFAULT_VOICE)
    if not text:
        return JSONResponse(status_code=400, content={"error": "Text is required"})
    res = await VoiceEngine.speak_on_pc(text, voice)
    return {"success": res, "text": text, "voice": voice}

@app.get("/api/voice/voices")
async def api_voice_voices():
    from core.voice_engine import VoiceEngine
    return {"voices": VoiceEngine.list_voices()}

@app.get("/api/mcp/servers")
async def api_mcp_servers():
    from core.mcp_manager import MCPManager
    return {"servers": MCPManager.get_instance().list_servers()}

@app.get("/api/mcp/tools")
async def api_mcp_tools():
    from core.mcp_manager import MCPManager
    tools = await MCPManager.get_instance().list_tools_async()
    return {"tools": tools}

# Mount screenshots directory
screenshots_dir = Path(__file__).parent / "screenshots"
screenshots_dir.mkdir(parents=True, exist_ok=True)
app.mount("/screenshots", StaticFiles(directory=str(screenshots_dir)), name="screenshots")

# Mount static files and serve index.html
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def serve_index():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Helper-AI API running. Static UI not yet created."}

def run_server(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True):
    import uvicorn
    if open_browser:
        async def open_tab():
            await asyncio.sleep(1.2)
            webbrowser.open(f"http://{host}:{port}")
        loop = asyncio.new_event_loop()
        import threading
        t = threading.Thread(target=lambda: (webbrowser.open(f"http://{host}:{port}")))
        t.daemon = True
        # Schedule browser opening after server binds
        import time
        threading.Timer(1.0, lambda: webbrowser.open(f"http://{host}:{port}")).start()

    uvicorn.run("app:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    run_server(host=host, port=port, open_browser=True)
