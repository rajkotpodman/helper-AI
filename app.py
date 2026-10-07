"""Helper-AI: Web Dashboard and API Server."""
import os
import sys
import json
import asyncio
import webbrowser
from pathlib import Path
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

app = FastAPI(title="Helper-AI Dashboard")

# Global agent manager state
active_agent: HelperAgent = None
active_task: asyncio.Task = None
connected_websockets: list[WebSocket] = []
current_goal_info = {
    "is_running": False,
    "goal": "",
    "history": []
}

class GoalRequest(BaseModel):
    goal: str
    provider: str = None
    safe_mode: bool = False
    max_steps: int = 25

class SettingsRequest(BaseModel):
    provider: str
    gemini_key: str = None
    openai_key: str = None
    groq_key: str = None
    ollama_url: str = None
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
        "has_gemini_key": bool(os.getenv("GEMINI_API_KEY")),
        "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "has_groq_key": bool(os.getenv("GROQ_API_KEY"))
    }

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

@app.post("/api/run")
async def start_goal(req: GoalRequest):
    global active_agent, active_task, current_goal_info

    if current_goal_info["is_running"]:
        return JSONResponse(status_code=400, content={"error": "An agent task is already actively running."})

    goal_str = req.goal.strip()
    if not goal_str:
        return JSONResponse(status_code=400, content={"error": "Goal cannot be empty."})

    llm = LLMClient(provider=req.provider)
    active_agent = HelperAgent(llm_client=llm, safe_mode=req.safe_mode, max_steps=req.max_steps)

    current_goal_info["is_running"] = True
    current_goal_info["goal"] = goal_str
    current_goal_info["history"] = []

    async def run_worker():
        global active_agent, current_goal_info
        try:
            async def on_event(ev_type: str, data: dict):
                await broadcast_event(ev_type, data)
                if ev_type == "action_result":
                    current_goal_info["history"].append(data)

            result = await active_agent.run(goal_str, on_event=on_event)
            await broadcast_event("finished", result)
        except Exception as e:
            await broadcast_event("error", {"error": str(e)})
        finally:
            current_goal_info["is_running"] = False

    active_task = asyncio.create_task(run_worker())
    return {"success": True, "message": "Agent execution initiated."}

@app.post("/api/cancel")
async def cancel_goal():
    global active_agent, current_goal_info
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

    os.environ["SAFE_MODE"] = str(req.safe_mode).lower()
    set_key(str(env_file), "SAFE_MODE", str(req.safe_mode).lower())

    return {"success": True, "message": "Settings updated successfully."}

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
