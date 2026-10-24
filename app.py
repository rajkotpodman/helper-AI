"""Helper-AI: Web Dashboard and API Server."""
import os
import sys
import json
import asyncio
import webbrowser
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv, set_key
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

load_dotenv(override=True)

from core.agent import HelperAgent
from core.llm import LLMClient
from core.tools import ToolRegistry
from core.metrics import metrics
from core.audit import audit_logger
from core.permissions import PermissionManager
from core.memory_recorder import MarkdownMemoryRecorder

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Helper-AI Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GLOBAL_TOOLS = ToolRegistry()

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
    image_data: Optional[str] = None

class VisionAnalyzeRequest(BaseModel):
    image_data: str
    prompt: Optional[str] = ""

class PermissionRespondRequest(BaseModel):
    request_id: str
    approved: bool

class SettingsRequest(BaseModel):
    provider: str
    anthropic_key: Optional[str] = None
    anthropic_model: Optional[str] = None
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
    unrestricted_mode: Optional[bool] = True
    background_ai_provider: Optional[str] = "auto"

class ChooseAIRequest(BaseModel):
    primary_provider: Optional[str] = None
    primary_model: Optional[str] = None
    background_provider: Optional[str] = None

class BackgroundConsultRequest(BaseModel):
    query: str
    provider: Optional[str] = "auto"
    role: Optional[str] = "advisor"
    context: Optional[str] = None

class SwarmRequest(BaseModel):
    query: str
    providers: Optional[List[str]] = None
    role: Optional[str] = "consensus"

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
    return {
        "is_running": current_goal_info["is_running"],
        "goal": current_goal_info["goal"],
        "tools_count": len(GLOBAL_TOOLS.get_all_tools()),
        "provider": os.getenv("LLM_PROVIDER", "gemini"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "dolphin-llama3"),
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
    return {"tools": GLOBAL_TOOLS.get_schemas()}

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

    try:
        llm = LLMClient(provider=req.provider)
        active_agent = HelperAgent(
            llm_client=llm,
            safe_mode=req.safe_mode,
            max_steps=steps,
            permission_manager=permission_manager,
            memory_recorder=memory_recorder
        )
    except Exception as init_err:
        logger.error(f"Failed to initialize HelperAgent: {init_err}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"Agent initialization failed: {str(init_err)}"})

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

            result = await active_agent.run(goal_str, on_event=on_event, image_data=req.image_data)
            if active_agent and active_agent._should_cancel:
                await broadcast_event("cancelled", {"message": "Goal was stopped by user."})
            else:
                await broadcast_event("finished", result or {"success": True, "message": "Goal finished."})
        except asyncio.CancelledError:
            logger.info("Agent task was cancelled by user.")
            await broadcast_event("cancelled", {"message": "Goal was stopped by user."})
        except Exception as e:
            logger.error(f"Exception during agent run: {e}", exc_info=True)
            await broadcast_event("error", {"error": str(e)})
        finally:
            current_goal_info["is_running"] = False

    active_task = asyncio.create_task(run_worker())
    return {"success": True, "message": "Agent execution initiated."}

@app.post("/api/vision/analyze")
async def analyze_vision_endpoint(req: VisionAnalyzeRequest):
    from core.vision_engine import vision_engine
    return vision_engine.analyze_image_with_ai(base64_data=req.image_data, goal=req.prompt or "")


@app.post("/api/cancel")
async def cancel_goal():
    global active_agent, active_task, current_goal_info
    permission_manager.cancel_all()
    try:
        from core.job_portal_automation import job_portal_automation
        job_portal_automation.cancel()
    except Exception:
        pass

    was_running = current_goal_info.get("is_running", False) or (active_task and not active_task.done())
    if active_agent:
        active_agent.cancel()
    if active_task and not active_task.done():
        active_task.cancel()
    current_goal_info["is_running"] = False

    if was_running:
        await broadcast_event("cancelled", {"message": "User stopped execution."})
        return {"success": True, "message": "Agent cancel signal sent."}
    return {"success": False, "message": "No active agent running."}


@app.get("/api/settings")
async def get_settings():
    return {
        "provider": os.getenv("LLM_PROVIDER", "gemini").strip("'\""),
        "anthropic_key": os.getenv("ANTHROPIC_API_KEY", "").strip("'\""),
        "anthropic_model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022").strip("'\""),
        "gemini_key": os.getenv("GEMINI_API_KEY", "").strip("'\""),
        "groq_key": os.getenv("GROQ_API_KEY", "").strip("'\""),
        "openai_key": os.getenv("OPENAI_API_KEY", "").strip("'\""),
        "deepseek_key": os.getenv("DEEPSEEK_API_KEY", "").strip("'\""),
        "custom_name": os.getenv("CUSTOM_LLM_NAME", "OpenRouter").strip("'\""),
        "custom_url": os.getenv("CUSTOM_LLM_URL", "https://openrouter.ai/api/v1").strip("'\""),
        "custom_key": os.getenv("CUSTOM_LLM_KEY", "").strip("'\""),
        "custom_model": os.getenv("CUSTOM_LLM_MODEL", "anthropic/claude-3.5-sonnet").strip("'\""),
        "ollama_model": os.getenv("OLLAMA_MODEL", "dolphin-llama3").strip("'\""),
        "safe_mode": os.getenv("SAFE_MODE", "false").strip("'\"").lower() == "true",
        "unrestricted_mode": permission_manager.is_unrestricted(),
        "background_ai_provider": os.getenv("BACKGROUND_AI_PROVIDER", "auto").strip("'\"")
    }

@app.post("/api/settings")
async def update_settings(req: SettingsRequest):
    env_file = Path.cwd() / ".env"
    if not env_file.exists():
        env_file.touch()

    if req.provider:
        os.environ["LLM_PROVIDER"] = req.provider
        set_key(str(env_file), "LLM_PROVIDER", req.provider)
    if req.anthropic_key is not None:
        os.environ["ANTHROPIC_API_KEY"] = req.anthropic_key
        set_key(str(env_file), "ANTHROPIC_API_KEY", req.anthropic_key)
    if req.anthropic_model is not None:
        os.environ["ANTHROPIC_MODEL"] = req.anthropic_model
        set_key(str(env_file), "ANTHROPIC_MODEL", req.anthropic_model)
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

    if req.unrestricted_mode is not None:
        permission_manager.set_unrestricted_mode(req.unrestricted_mode)
        os.environ["HELPER_UNRESTRICTED_ACCESS"] = str(req.unrestricted_mode).lower()
        set_key(str(env_file), "HELPER_UNRESTRICTED_ACCESS", str(req.unrestricted_mode).lower())

    if req.background_ai_provider is not None:
        from core.background_ai_swarm import background_ai_swarm
        background_ai_swarm.set_background_provider(req.background_ai_provider)
        set_key(str(env_file), "BACKGROUND_AI_PROVIDER", req.background_ai_provider)

    return {"success": True, "message": "Settings updated successfully."}

@app.get("/api/ai/providers")
async def get_ai_providers():
    from core.background_ai_swarm import background_ai_swarm
    return {
        "providers": background_ai_swarm.get_available_providers(),
        "active_primary": os.getenv("LLM_PROVIDER", "gemini"),
        "active_background": os.getenv("BACKGROUND_AI_PROVIDER", "auto"),
        "unrestricted_access": permission_manager.is_unrestricted()
    }

@app.post("/api/ai/choose")
async def choose_ai(req: ChooseAIRequest):
    from core.background_ai_swarm import background_ai_swarm
    env_file = Path.cwd() / ".env"
    res = {}
    if req.primary_provider:
        res["primary"] = background_ai_swarm.set_primary_provider(req.primary_provider, req.primary_model)
        set_key(str(env_file), "LLM_PROVIDER", req.primary_provider)
        if req.primary_model:
            set_key(str(env_file), f"{req.primary_provider.upper()}_MODEL", req.primary_model)
    if req.background_provider:
        res["background"] = background_ai_swarm.set_background_provider(req.background_provider)
        set_key(str(env_file), "BACKGROUND_AI_PROVIDER", req.background_provider)
    await broadcast_event("ai_provider_switched", res)
    return {"success": True, "details": res}

@app.post("/api/ai/background-consult")
async def consult_background_ai_endpoint(req: BackgroundConsultRequest):
    from core.background_ai_swarm import background_ai_swarm
    result = await asyncio.to_thread(
        background_ai_swarm.consult,
        query=req.query,
        provider=req.provider,
        role=req.role or "advisor",
        context=req.context
    )
    return result

@app.post("/api/ai/swarm")
async def swarm_consensus_endpoint(req: SwarmRequest):
    from core.background_ai_swarm import background_ai_swarm
    result = await asyncio.to_thread(
        background_ai_swarm.consult_swarm,
        query=req.query,
        providers=req.providers,
        role=req.role or "consensus"
    )
    return result

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
    def _read_stats():
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage(str(Path.cwd().anchor))
        except Exception:
            cpu = 0.0
            mem = type("Obj", (), {"percent": 0.0, "used": 0, "total": 0})()
            disk = type("Obj", (), {"percent": 0.0, "free": 0})()
        return cpu, mem, disk

    cpu, mem, disk = await asyncio.to_thread(_read_stats)

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
        "tools_registered": len(GLOBAL_TOOLS.get_all_tools()),
        "memory_file_size_mb": memory_recorder.get_size_mb(),
        "memory_entries": memory_recorder.get_entry_count(),
        "provider": os.getenv("LLM_PROVIDER", "gemini"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "dolphin-llama3"),
        "safe_mode": os.getenv("SAFE_MODE", "false").lower() == "true"
    }

@app.get("/api/ollama/status")
async def get_ollama_status():
    from core.auto_setup_ollama import OllamaAutoSetup
    def _check():
        installed = OllamaAutoSetup.is_ollama_installed()
        running = OllamaAutoSetup.is_server_running() if installed else False
        models = OllamaAutoSetup.get_installed_models() if running else []
        dolphin_ready = any("dolphin" in m.lower() for m in models)
        return {
            "installed": installed,
            "running": running,
            "models": models,
            "dolphin_ready": dolphin_ready,
            "active_model": os.getenv("OLLAMA_MODEL", "dolphin-llama3"),
            "provider": os.getenv("LLM_PROVIDER", "gemini")
        }
    return await asyncio.to_thread(_check)

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

class LiveKitTokenRequest(BaseModel):
    room: Optional[str] = None
    identity: Optional[str] = None
    name: Optional[str] = None

class LiveKitToolRequest(BaseModel):
    tool: str
    arguments: Optional[Dict[str, Any]] = None

@app.get("/api/livekit/status")
async def get_livekit_status():
    from core.livekit_bridge import livekit_bridge
    return livekit_bridge.get_status()

@app.post("/api/livekit/token")
async def get_livekit_token(req: LiveKitTokenRequest):
    from core.livekit_bridge import livekit_bridge
    return livekit_bridge.generate_token(room_name=req.room, identity=req.identity, name=req.name)

@app.post("/api/livekit/session/start")
async def start_livekit_session(req: LiveKitTokenRequest):
    from core.livekit_bridge import livekit_bridge
    return livekit_bridge.start_session(room_name=req.room)

@app.post("/api/livekit/session/stop")
async def stop_livekit_session():
    from core.livekit_bridge import livekit_bridge
    return livekit_bridge.stop_session()

@app.post("/api/livekit/execute-tool")
async def execute_livekit_tool(req: LiveKitToolRequest):
    from core.livekit_bridge import livekit_bridge
    return await livekit_bridge.execute_tool_from_voice(req.tool, req.arguments or {})

# --- Voice Engine & Hands-Free Voice Agent ---
class VoiceSynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = "en-US-AriaNeural"
    rate: Optional[str] = "+0%"
    pitch: Optional[str] = "+0Hz"

class VoiceDispatchRequest(BaseModel):
    transcript: str
    voice: Optional[str] = "en-US-AriaNeural"
    speak_on_pc: Optional[bool] = False
    provider: Optional[str] = "gemini"

@app.get("/api/voice/voices")
async def list_available_voices():
    """List available neural voices supported by Helper-AI Voice Engine."""
    from core.voice_engine import VoiceEngine
    return {"voices": VoiceEngine.list_voices()}

@app.post("/api/voice/synthesize")
async def synthesize_voice_audio(req: VoiceSynthesizeRequest):
    """Synthesizes text into high-definition neural MP3 audio stream."""
    from core.voice_engine import VoiceEngine, DEFAULT_VOICE
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    voice = req.voice or DEFAULT_VOICE
    audio_bytes = await VoiceEngine.synthesize_to_bytes(req.text, voice=voice, rate=req.rate or "+0%", pitch=req.pitch or "+0Hz")
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Speech synthesis failed.")
    return Response(content=audio_bytes, media_type="audio/mpeg", headers={
        "Content-Disposition": "inline; filename=speech.mp3",
        "Cache-Control": "max-age=3600"
    })

@app.post("/api/voice/speak")
async def speak_text_on_pc(payload: Dict[str, Any]):
    """Read aloud text using Edge-TTS or system speech directly on PC speakers."""
    from core.voice_engine import VoiceEngine, DEFAULT_VOICE
    text = payload.get("text", "")
    voice = payload.get("voice", DEFAULT_VOICE)
    if not text:
        return JSONResponse(status_code=400, content={"error": "Text is required"})
    res = await VoiceEngine.speak_on_pc(text, voice)
    return {"success": res, "text": text, "voice": voice}

@app.post("/api/voice/dispatch")
async def dispatch_voice_command(req: VoiceDispatchRequest):
    """Processes hands-free spoken user commands and generates a conversational speech reply."""
    from core.voice_engine import VoiceEngine, DEFAULT_VOICE
    import base64
    import psutil
    import time

    transcript = (req.transcript or "").strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript is required.")

    voice = req.voice or DEFAULT_VOICE
    t_lower = transcript.lower()
    tool_executed = None
    spoken_reply = ""
    full_output = ""

    if any(k in t_lower for k in ["cpu", "ram", "memory", "health", "system"]):
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        tool_executed = "get_system_health"
        spoken_reply = f"Your system is running smoothly. CPU usage is currently {cpu} percent, and RAM usage is at {mem} percent."
        full_output = spoken_reply
    elif "time" in t_lower:
        now_str = time.strftime("%I:%M %p")
        spoken_reply = f"The current local time is {now_str}."
        full_output = spoken_reply
    else:
        try:
            llm = LLMClient(provider=req.provider or "gemini")
            sys_prompt = (
                "You are Helper-AI's Voice Persona. The user just spoke to you via hands-free microphone. "
                "Provide a crisp, direct, helpful spoken response (1 to 3 short sentences max). "
                "Never use markdown asterisks, bullet points, emojis, or code blocks in spoken responses."
            )
            spoken_reply = await asyncio.to_thread(
                llm.complete,
                f"{sys_prompt}\n\nUser Spoke: {transcript}"
            )
            spoken_reply = spoken_reply.replace("*", "").replace("#", "").replace("`", "").strip()
            full_output = spoken_reply
        except Exception as e:
            spoken_reply = f"I heard your request: {transcript}. However, my language service encountered a momentary issue."
            full_output = spoken_reply

    audio_bytes = await VoiceEngine.synthesize_to_bytes(spoken_reply, voice=voice)
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8") if audio_bytes else ""

    if req.speak_on_pc:
        asyncio.create_task(VoiceEngine.speak_on_pc(spoken_reply, voice=voice))

    return {
        "success": True,
        "transcript": transcript,
        "reply": spoken_reply,
        "full_output": full_output,
        "tool_executed": tool_executed,
        "audio_base64": audio_b64,
        "voice": voice
    }


# --- Microsoft Playwright CRM & Heavy Automation Endpoints ---
class PlaywrightLaunchRequest(BaseModel):
    url: Optional[str] = None
    workflow_name: Optional[str] = None
    target_lang: Optional[str] = "python"
    use_chrome: Optional[bool] = True
    save_session: Optional[bool] = True
    session_name: Optional[str] = "tata_crm_session"

class PlaywrightWorkflowSaveRequest(BaseModel):
    name: str
    code: str

class PlaywrightWorkflowRunRequest(BaseModel):
    name: str
    data_records: Optional[List[Dict[str, Any]]] = None
    delay_between_records_s: Optional[float] = 1.0
    timeout_seconds: Optional[int] = 180

@app.get("/api/playwright/status")
async def get_playwright_status():
    """Returns Playwright installation, active Codegen state, and available workflows."""
    from core.playwright_manager import playwright_manager
    return playwright_manager.get_status()

@app.post("/api/playwright/codegen/launch")
async def launch_playwright_codegen_endpoint(req: PlaywrightLaunchRequest):
    """Launches Playwright Codegen recorder with real Google Chrome."""
    from core.playwright_manager import playwright_manager
    return playwright_manager.launch_codegen(
        url=req.url,
        workflow_name=req.workflow_name,
        target_lang=req.target_lang or "python",
        use_chrome=bool(req.use_chrome),
        save_session=bool(req.save_session),
        session_name=req.session_name
    )

@app.post("/api/playwright/codegen/stop")
async def stop_playwright_codegen_endpoint():
    """Stops active Playwright Codegen recorder session."""
    from core.playwright_manager import playwright_manager
    return playwright_manager.stop_codegen()

@app.get("/api/playwright/workflows")
async def list_playwright_workflows_endpoint():
    """Lists all recorded Playwright automation workflows."""
    from core.playwright_manager import playwright_manager
    return {"workflows": playwright_manager.list_workflows()}

@app.get("/api/playwright/workflows/{name}")
async def get_playwright_workflow_endpoint(name: str):
    """Fetches code content for a given workflow script."""
    from core.playwright_manager import playwright_manager
    return playwright_manager.get_workflow(name)

@app.post("/api/playwright/workflows/save")
async def save_playwright_workflow_endpoint(req: PlaywrightWorkflowSaveRequest):
    """Saves or updates a workflow Python script."""
    from core.playwright_manager import playwright_manager
    return playwright_manager.save_workflow(req.name, req.code)

@app.post("/api/playwright/workflows/run")
async def run_playwright_workflow_endpoint(req: PlaywrightWorkflowRunRequest):
    """Runs a Playwright workflow standalone or in batch mode over Excel/CSV data records."""
    from core.playwright_manager import playwright_manager
    if req.data_records and len(req.data_records) > 0:
        return playwright_manager.run_workflow_batch(
            name=req.name,
            data_records=req.data_records,
            delay_between_records_s=req.delay_between_records_s or 1.0
        )
    return playwright_manager.run_workflow_standalone(
        name=req.name,
        timeout_seconds=req.timeout_seconds or 180
    )


class JobPortalProcessRequest(BaseModel):
    cv_path: Optional[str] = None
    portal_id: Optional[str] = None

class JobPortalOTPRequest(BaseModel):
    otp: str
    portal_id: Optional[str] = None

@app.get("/api/job-portals/status")
async def get_job_portals_status():
    """Returns candidate CV data and status of all 10 job portals."""
    from core.job_portal_automation import job_portal_automation
    cv_data = job_portal_automation.parse_cv_details()
    portals = job_portal_automation.get_portals()
    return {
        "candidate": cv_data,
        "portals": portals
    }

@app.post("/api/job-portals/process")
async def process_job_portals_endpoint(req: JobPortalProcessRequest):
    """Executes automated registration and CV upload across job portals."""
    from core.job_portal_automation import job_portal_automation
    if req.portal_id:
        return job_portal_automation.register_and_upload(req.portal_id, req.cv_path)
    return job_portal_automation.process_all_10_portals(req.cv_path)

@app.post("/api/job-portals/submit-otp")
async def submit_job_portal_otp_endpoint(req: JobPortalOTPRequest):
    """Submits the OTP code into the currently active portal verification page."""
    from core.job_portal_automation import job_portal_automation
    res = job_portal_automation.enter_otp(req.otp, req.portal_id)
    return res



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

wetware_dist_dir = base_dir / "ai_2026_hub" / "dist"
wetware_assets_dir = wetware_dist_dir / "assets"

if wetware_assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(wetware_assets_dir)), name="wetware-assets")

if wetware_dist_dir.exists():
    app.mount("/wetware-hub", StaticFiles(directory=str(wetware_dist_dir), html=True), name="wetware-hub")

@app.get("/wetware")
async def serve_wetware():
    if wetware_dist_dir.exists():
        index_f = wetware_dist_dir / "index.html"
        if index_f.exists():
            return FileResponse(index_f)
    return {"message": "AI 2026 Wetware Hub build not found."}

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
