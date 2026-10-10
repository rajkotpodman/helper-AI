"""Desktop GUI & Native Windows Automation Tool for Helper-AI.

Integrates pywinauto and pyautogui for native Windows application control,
window automation, keyboard shortcuts, mouse clicks, and desktop screenshots.
"""
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import pyautogui
pyautogui.FAILSAFE = False

try:
    import pywinauto
    HAS_PYWINAUTO = True
except ImportError:
    HAS_PYWINAUTO = False

from core.tools.base import BaseTool

logger = logging.getLogger("DesktopGUITool")


class DesktopGUIControlTool(BaseTool):
    """Controls native Windows GUI applications, mouse, and keyboard."""
    name = "desktop_gui_control"
    description = (
        "Controls native Windows GUI software, mouse, and keyboard. "
        "Can launch native apps, send keystrokes and keyboard shortcuts (like Ctrl+S, Enter, Tab), "
        "click screen positions, capture screenshots, and query screen resolution."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": (
                    "Action to perform: 'send_keys' (type text or shortcuts), 'press_key' (single key press), "
                    "'click_screen' (click at x, y), 'get_screen_info' (screen resolution and mouse pos), "
                    "'start_app' (launch GUI application via pywinauto), 'take_screenshot' (capture desktop image)"
                ),
                "enum": [
                    "send_keys",
                    "press_key",
                    "click_screen",
                    "get_screen_info",
                    "start_app",
                    "take_screenshot"
                ]
            },
            "text": {
                "type": "string",
                "description": "Text or characters to type for send_keys action."
            },
            "key": {
                "type": "string",
                "description": "Key to press for press_key action (e.g. 'enter', 'tab', 'esc', 'win', 'f5', 'ctrl')."
            },
            "x": {
                "type": "integer",
                "description": "X coordinate in pixels on screen for click_screen action."
            },
            "y": {
                "type": "integer",
                "description": "Y coordinate in pixels on screen for click_screen action."
            },
            "app_path": {
                "type": "string",
                "description": "Application executable path or command for start_app action (e.g. 'notepad.exe', 'calc.exe')."
            },
            "filename": {
                "type": "string",
                "description": "Optional custom filename for take_screenshot action."
            }
        },
        "required": ["action"]
    }

    def execute(
        self,
        action: str,
        text: Optional[str] = None,
        key: Optional[str] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        app_path: Optional[str] = None,
        filename: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        try:
            if action == "get_screen_info":
                w, h = pyautogui.size()
                mx, my = pyautogui.position()
                return {
                    "success": True,
                    "resolution": {"width": w, "height": h},
                    "mouse_position": {"x": mx, "y": my},
                    "output": f"Screen resolution: {w}x{h}. Cursor currently at: ({mx}, {my})."
                }

            elif action == "send_keys":
                content = text or kwargs.get("content") or kwargs.get("keys") or ""
                if not content:
                    return {"success": False, "output": "Please specify 'text' to type."}
                pyautogui.write(content, interval=0.03)
                return {
                    "success": True,
                    "output": f"Sent keystrokes: '{content}' to active window.",
                    "text": content
                }

            elif action == "press_key":
                target_key = key or kwargs.get("k") or "enter"
                pyautogui.press(target_key)
                return {
                    "success": True,
                    "output": f"Pressed key '{target_key}'.",
                    "key": target_key
                }

            elif action == "click_screen":
                if x is None or y is None:
                    return {"success": False, "output": "Please specify both 'x' and 'y' pixel coordinates."}
                pyautogui.click(x=x, y=y)
                return {
                    "success": True,
                    "output": f"Clicked at coordinates ({x}, {y}) on screen.",
                    "coordinates": {"x": x, "y": y}
                }

            elif action == "start_app":
                target = app_path or kwargs.get("target") or "notepad.exe"
                if not HAS_PYWINAUTO:
                    return {"success": False, "output": "pywinauto is not installed."}
                app = pywinauto.Application(backend="win32").start(target)
                time.sleep(1.0)
                return {
                    "success": True,
                    "output": f"Successfully launched native Windows application '{target}' (PID: {app.process}).",
                    "pid": app.process
                }

            elif action == "take_screenshot":
                screenshots_dir = Path("screenshots")
                screenshots_dir.mkdir(parents=True, exist_ok=True)
                fn = filename or f"screenshot_{int(time.time())}.png"
                out_path = screenshots_dir / fn
                pyautogui.screenshot(str(out_path))
                return {
                    "success": True,
                    "output": f"Desktop screenshot saved to '{out_path.resolve()}'.",
                    "file_path": str(out_path.resolve())
                }

            else:
                return {
                    "success": False,
                    "output": f"Unknown desktop GUI action: '{action}'. Available: send_keys, press_key, click_screen, get_screen_info, start_app, take_screenshot."
                }

        except Exception as e:
            logger.error(f"DesktopGUIControlTool error: {e}", exc_info=True)
            return {
                "success": False,
                "output": f"Desktop GUI control error: {str(e)}",
                "error": str(e)
            }
