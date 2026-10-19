"""Playwright Vision Browser Tool for Helper-AI.

Allows Helper-AI to inspect web pages, capture screenshots, and perform precision
DOM interactions using Playwright over Chrome DevTools Protocol (CDP).
"""
import asyncio
from typing import Dict, Any, Optional, List
from core.tools.base import BaseTool
from core.playwright_agent import PlaywrightVisionAgent


class VisionBrowserTool(BaseTool):
    """Advanced Playwright Vision & DOM Browser Automation Tool."""
    name = "vision_browser"
    description = (
        "Advanced Playwright Vision & DOM browser automation tool. "
        "Allows visual screenshot captures, accessibility element inspection, "
        "and precision clicking/typing directly on the persistent live Chrome browser via CDP."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to perform: 'navigate', 'get_elements', 'click', 'type', 'screenshot'",
                "enum": ["navigate", "get_elements", "click", "type", "screenshot"]
            },
            "url": {
                "type": "string",
                "description": "The URL to visit (for navigate action)."
            },
            "target": {
                "type": "string",
                "description": "Element name, text, placeholder, or selector to click or type into."
            },
            "text": {
                "type": "string",
                "description": "Text to enter into the targeted input field (for type action)."
            },
            "press_enter": {
                "type": "boolean",
                "description": "Whether to press Enter after typing text.",
                "default": False
            },
            "filename": {
                "type": "string",
                "description": "Optional custom filename for screenshot (e.g. 'page_preview.png')."
            }
        },
        "required": ["action"]
    }

    def execute(
        self,
        action: str,
        url: Optional[str] = None,
        target: Optional[str] = None,
        text: Optional[str] = None,
        press_enter: bool = False,
        filename: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        agent = PlaywrightVisionAgent.get_instance()

        def _run_async(coro):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        return pool.submit(lambda: asyncio.run(coro)).result()
                else:
                    return loop.run_until_complete(coro)
            except Exception:
                return asyncio.run(coro)

        try:
            if action == "navigate":
                dest_url = url or kwargs.get("link") or "https://www.google.com"
                return _run_async(agent.navigate(dest_url))

            elif action in ["get_elements", "inspect_page", "scan_page"]:
                return _run_async(agent.get_interactive_elements())

            elif action == "click":
                if not target:
                    return {"success": False, "output": "Please specify 'target' text or selector to click."}
                return _run_async(agent.click(target))

            elif action == "type":
                if not target:
                    return {"success": False, "output": "Please specify 'target' input field to type into."}
                return _run_async(agent.type_text(target, text or "", press_enter=press_enter))

            elif action == "screenshot":
                return _run_async(agent.take_screenshot(filename))

            else:
                return {
                    "success": False,
                    "output": f"Unknown vision_browser action: '{action}'. Available: navigate, get_elements, click, type, screenshot."
                }

        except Exception as e:
            return {
                "success": False,
                "output": f"Vision browser error: {str(e)}",
                "error": str(e)
            }


class PlaywrightCodegenTool(BaseTool):
    """Playwright Codegen Live Recording Tool for CRM & Web Portals."""
    name = "playwright_codegen"
    description = (
        "Launches Microsoft Playwright Codegen in real Google Chrome with the Playwright Inspector. "
        "Allows user to click and fill forms in any CRM or web portal while Playwright writes the automation code live."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action: 'launch', 'stop', or 'status'",
                "enum": ["launch", "stop", "status"]
            },
            "url": {
                "type": "string",
                "description": "Starting portal or CRM URL (e.g. Tata CRM login or form URL)."
            },
            "workflow_name": {
                "type": "string",
                "description": "Name for the recorded workflow script (e.g. 'tata_crm_lead_entry')."
            },
            "use_chrome": {
                "type": "boolean",
                "description": "Whether to use Google Chrome instead of Chromium (default True).",
                "default": True
            },
            "save_session": {
                "type": "boolean",
                "description": "Whether to save cookies/session to avoid logging in again (default True).",
                "default": True
            }
        },
        "required": ["action"]
    }

    def execute(
        self,
        action: str,
        url: Optional[str] = None,
        workflow_name: Optional[str] = None,
        use_chrome: bool = True,
        save_session: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        from core.playwright_manager import playwright_manager
        if action == "launch":
            res = playwright_manager.launch_codegen(
                url=url,
                workflow_name=workflow_name,
                use_chrome=use_chrome,
                save_session=save_session
            )
            return {
                "success": res.get("success", False),
                "output": res.get("message") or res.get("error"),
                "details": res
            }
        elif action == "stop":
            res = playwright_manager.stop_codegen()
            return {"success": res["success"], "output": res.get("message") or res.get("error")}
        elif action == "status":
            st = playwright_manager.get_status()
            return {"success": True, "output": f"Playwright version: {st['version']}, Codegen running: {st['codegen_active']}, Workflows: {st['workflows_count']}", "status": st}
        else:
            return {"success": False, "output": f"Unknown action: {action}"}


class PlaywrightWorkflowTool(BaseTool):
    """Playwright Automation Workflow & CRM Batch Execution Tool."""
    name = "playwright_workflow"
    description = (
        "Lists, inspects, or executes recorded Playwright Python workflows. "
        "Supports standalone replay or batch execution over CSV/Excel lead data."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action: 'list', 'get', 'save', 'run_standalone', 'run_batch'",
                "enum": ["list", "get", "save", "run_standalone", "run_batch"]
            },
            "name": {
                "type": "string",
                "description": "Workflow script name (e.g. 'tata_crm_template.py')."
            },
            "code": {
                "type": "string",
                "description": "Code content to save (for action 'save')."
            },
            "data_records": {
                "type": "array",
                "items": {"type": "object"},
                "description": "List of record dictionaries for batch form filling (for action 'run_batch')."
            }
        },
        "required": ["action"]
    }

    def execute(
        self,
        action: str,
        name: Optional[str] = None,
        code: Optional[str] = None,
        data_records: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        from core.playwright_manager import playwright_manager

        if action == "list":
            wf = playwright_manager.list_workflows()
            return {"success": True, "output": f"Found {len(wf)} Playwright workflows.", "workflows": wf}

        elif action == "get":
            if not name:
                return {"success": False, "output": "Parameter 'name' is required for get action."}
            res = playwright_manager.get_workflow(name)
            return {"success": res.get("success", False), "output": f"Retrieved {name}", "workflow": res}

        elif action == "save":
            if not name or code is None:
                return {"success": False, "output": "Parameters 'name' and 'code' are required for save action."}
            res = playwright_manager.save_workflow(name, code)
            return {"success": res.get("success", False), "output": res.get("message"), "path": res.get("path")}

        elif action == "run_standalone":
            if not name:
                return {"success": False, "output": "Parameter 'name' is required for run_standalone action."}
            res = playwright_manager.run_workflow_standalone(name)
            return {
                "success": res.get("success", False),
                "output": res.get("output") or res.get("error"),
                "result": res
            }

        elif action == "run_batch":
            if not name or not data_records:
                return {"success": False, "output": "Parameters 'name' and 'data_records' are required for run_batch."}
            res = playwright_manager.run_workflow_batch(name, data_records)
            return {
                "success": res.get("success", False),
                "output": f"Batch completed: {res.get('completed_rows')}/{res.get('total_rows')} rows filled successfully.",
                "result": res
            }

        else:
            return {"success": False, "output": f"Unknown action: {action}"}

