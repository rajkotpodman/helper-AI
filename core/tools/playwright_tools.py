"""Playwright Vision Browser Tool for Helper-AI.

Allows Helper-AI to inspect web pages, capture screenshots, and perform precision
DOM interactions using Playwright over Chrome DevTools Protocol (CDP).
"""
import asyncio
from typing import Dict, Any, Optional
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
