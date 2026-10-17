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
    deepseek_key: Optional[str] = None
    custom_name: Optional[str] = None
    custom_url: Optional[str] = None
    custom_key: Optional[str] = None
    custom_model: Optional[str] = None
    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None
    safe_mode: bool = False

class TranslateRequest(BaseModel):
    text: Optional[str] = ""
    texts: Optional[List[str]] = None
    target_lang: str = "en"
    source_lang: Optional[str] = "auto"

async def broadcast_event(event_type: str, data: dict):
    payload = {"event": event_type, "type": event_type}
    if isinstance(data, dict):
        payload.update(data)
        payload["data"] = data
    else:
        payload["data"] = data
    message = json.dumps(payload)
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
            "history_count": len(current_goal_info["history"]),
            "history": current_goal_info["history"]
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
        "has_groq_key": bool(os.getenv("GROQ_API_KEY")),
        "has_deepseek_key": bool(os.getenv("DEEPSEEK_API_KEY")),
        "has_custom_ai": bool(os.getenv("CUSTOM_LLM_URL") or os.getenv("CUSTOM_LLM_KEY")),
        "custom_name": os.getenv("CUSTOM_LLM_NAME", "Universal AI"),
        "custom_model": os.getenv("CUSTOM_LLM_MODEL", "default")
    }

@app.get("/api/connections/check")
@app.get("/api/check-connections")
async def check_all_connections(pass_count: int = 2):
    """Diagnoses and tests all connections (Internet, Google Translate, LLM APIs, Chrome CDP, MCP, WebSocket)."""
    from core.connection_checker import connection_checker
    if pass_count >= 2:
        return connection_checker.check_twice()
    return connection_checker.check_all()


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

@app.get("/api/memory/stats")
@app.get("/api/memory/status")
async def get_memory_status():
    return {
        "file_path": str(memory_recorder.file_path),
        "file_name": memory_recorder.file_path.name,
        "size_bytes": memory_recorder.get_size_bytes(),
        "size_mb": memory_recorder.get_size_mb(),
        "limit_mb": round(memory_recorder.max_bytes / (1024 * 1024), 1),
        "total_prompts": memory_recorder.get_entry_count(),
        "prompt_count": memory_recorder.get_entry_count(),
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

@app.post("/api/execute")
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

@app.get("/api/translate/languages")
async def api_translate_languages():
    from core.translator import translator
    return {"languages": translator.get_supported_languages()}

@app.post("/api/translate")
async def api_translate(req: TranslateRequest):
    from core.translator import translator
    if req.texts:
        translated = translator.batch_translate(req.texts, target_lang=req.target_lang, source_lang=req.source_lang or "auto")
        return {"translated_texts": translated, "target_lang": req.target_lang}
    
    translated = translator.translate_text(req.text or "", target_lang=req.target_lang, source_lang=req.source_lang or "auto")
    return {"translated_text": translated, "target_lang": req.target_lang}

@app.get("/api/system-status")
async def get_system_status():
    import psutil, platform
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
        "provider": os.getenv("LLM_PROVIDER", "ollama"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "dolphin-llama3"),
        "safe_mode": os.getenv("SAFE_MODE", "false").lower() == "true"
    }

@app.get("/api/ollama/status")
async def get_ollama_status():
    from core.auto_setup_ollama import OllamaAutoSetup
    installed = OllamaAutoSetup.is_ollama_installed()
    running = OllamaAutoSetup.ensure_server_running() if installed else False
    models = OllamaAutoSetup.get_installed_models() if running else []
    dolphin_ready = any("dolphin" in m.lower() for m in models)
    return {
        "installed": installed,
        "running": running,
        "models": models,
        "dolphin_ready": dolphin_ready,
        "active_model": os.getenv("OLLAMA_MODEL", "dolphin-llama3"),
        "provider": os.getenv("LLM_PROVIDER", "ollama")
    }

@app.post("/api/setup/ollama-dolphin")
async def setup_ollama_dolphin():
    from core.auto_setup_ollama import OllamaAutoSetup
    result = await asyncio.to_thread(OllamaAutoSetup.run_full_setup, "dolphin-llama3")
    return result

@app.get("/api/quick-ideas")
async def get_quick_ideas():
    return {
        "ideas": [
            {"id": "google_blogs", "icon": "🌐", "title": "List My Google Blogs", "prompt": "give me the list of my google blogs"},
            {"id": "pc_health", "icon": "💻", "title": "PC Health Diagnostic", "prompt": "Check my PC health, CPU, RAM and disk usage"},
            {"id": "ai_research", "icon": "🔍", "title": "Web Research Report", "prompt": "Search the web for top 5 AI agent frameworks and write summary to Desktop"},
            {"id": "clean_downloads", "icon": "📁", "title": "Inspect Downloads", "prompt": "List the largest files in my Downloads folder"},
            {"id": "sysinfo_desktop", "icon": "📄", "title": "System Info to Desktop", "prompt": "Open PowerShell, test git version and write system info to Desktop/sysinfo.txt"},
            {"id": "reverse_engineer_app", "icon": "🧩", "title": "Reverse Engineer App", "prompt": "Reverse engineer Notepad, extract its UI automation controls, and save it to app memory"}
        ]
    }

class ReverseEngineerRequest(BaseModel):
    target: str
    depth: Optional[str] = "deep"
    save_to_memory: Optional[bool] = True

@app.get("/api/apps/memory")
async def list_app_memories():
    from core.reverse_engineering.app_memory_store import AppMemoryStore
    store = AppMemoryStore.get_instance()
    return {"profiles": store.list_all_profiles()}

@app.get("/api/apps/memory/{slug}")
async def get_app_memory(slug: str):
    from core.reverse_engineering.app_memory_store import AppMemoryStore
    store = AppMemoryStore.get_instance()
    prof = store.get_app_profile(slug)
    if not prof:
        return JSONResponse(status_code=404, content={"error": f"App '{slug}' not found in memory"})
    return {"profile": prof, "prompt": store.format_for_ai_prompt(prof)}

@app.post("/api/apps/reverse-engineer")
async def trigger_reverse_engineer(req: ReverseEngineerRequest):
    from core.reverse_engineering.app_analyzer import ReverseEngineeringEngine
    engine = ReverseEngineeringEngine.get_instance()
    result = await asyncio.to_thread(engine.reverse_engineer, target=req.target, depth=req.depth or "deep", save_to_memory=req.save_to_memory if req.save_to_memory is not None else True)
    return result

@app.get("/api/rea/status")
async def get_rea_status():
    from core.reverse_engineering.rea_bridge import REABridge
    bridge = REABridge.get_instance()
    return {
        "available": bridge.is_available(),
        "version": bridge.get_version(),
        "tools_count": len(bridge.list_mcp_tools())
    }

# Mount screenshots directory
screenshots_dir = Path(__file__).parent / "screenshots"
screenshots_dir.mkdir(parents=True, exist_ok=True)
app.mount("/screenshots", StaticFiles(directory=str(screenshots_dir)), name="screenshots")

# Mount static files and serve index.html (supports standard and PyInstaller frozen modes)
base_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
web_static_dir = base_dir / "web" / "static"
web_templates_dir = base_dir / "web" / "templates"
static_dir = base_dir / "static"
static_dir.mkdir(parents=True, exist_ok=True)

if web_static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_static_dir)), name="static")
else:
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def serve_index():
    modern_index = web_templates_dir / "index.html"
    if modern_index.exists():
        return FileResponse(modern_index)
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Helper-AI API running. Static UI not yet created."}

def run_server(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True):
    import uvicorn
    if open_browser:
        import threading
        # Schedule browser opening after server binds
        threading.Timer(1.2, lambda: webbrowser.open(f"http://{host}:{port}")).start()

    if getattr(sys, 'frozen', False):
        uvicorn.run(app, host=host, port=port)
    else:
        uvicorn.run("app:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    run_server(host=host, port=port, open_browser=True)
