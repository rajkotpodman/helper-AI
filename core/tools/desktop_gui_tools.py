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
        "Can launch native apps, send keystrokes and keyboard shortcuts (like Ctrl+S, Ctrl+C, Ctrl+V, Alt+Tab, Win+R), "
        "click/double-click/right-click screen positions, drag mouse, scroll mouse wheel, manage Windows clipboard, "
        "list open application windows, bring windows to front, and capture desktop screenshots."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": (
                    "Action to perform: 'send_keys' (type text), 'hotkey' (keyboard shortcut e.g. 'ctrl+c', 'ctrl+v', 'alt+tab', 'win+r'), "
                    "'press_key' (single key press e.g. 'enter', 'tab', 'esc'), 'click_screen' (left click at x, y), "
                    "'right_click' (right click at x, y), 'double_click' (double click at x, y), 'move_to' (move mouse to x, y), "
                    "'drag_to' (drag mouse to x, y), 'scroll' (scroll mouse wheel up/down), 'clipboard_copy' (copy text to clipboard), "
                    "'clipboard_paste' (read text from clipboard), 'list_windows' (list running application windows), "
                    "'focus_window' (bring window to front by title), 'start_app' (launch GUI application), 'take_screenshot' (capture screen)"
                ),
                "enum": [
                    "send_keys",
                    "type",
                    "write",
                    "hotkey",
                    "shortcut",
                    "press_key",
                    "enter",
                    "press_enter",
                    "click_screen",
                    "right_click",
                    "double_click",
                    "move_to",
                    "drag_to",
                    "scroll",
                    "clipboard_copy",
                    "clipboard_paste",
                    "list_windows",
                    "focus_window",
                    "get_screen_info",
                    "start_app",
                    "take_screenshot"
                ]
            },
            "text": {
                "type": "string",
                "description": "Text to type for send_keys or to copy to clipboard for clipboard_copy."
            },
            "keys": {
                "type": "string",
                "description": "Shortcut combination for hotkey action (e.g. 'ctrl+c', 'ctrl+v', 'alt+tab', 'win+r', 'ctrl+s', 'ctrl+a', 'alt+f4')."
            },
            "key": {
                "type": "string",
                "description": "Key to press for press_key action (e.g. 'enter', 'tab', 'esc', 'win', 'f5', 'ctrl', 'space', 'backspace')."
            },
            "x": {
                "type": "integer",
                "description": "X coordinate in pixels on screen for mouse actions."
            },
            "y": {
                "type": "integer",
                "description": "Y coordinate in pixels on screen for mouse actions."
            },
            "clicks": {
                "type": "integer",
                "description": "Scroll amount for scroll action (positive for scrolling up, negative for scrolling down, e.g. -500)."
            },
            "target": {
                "type": "string",
                "description": "Window title or application name to focus for focus_window."
            },
            "app_path": {
                "type": "string",
                "description": "Application executable path or command for start_app action (e.g. 'notepad.exe', 'calc.exe', 'mspaint.exe')."
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
        keys: Optional[str] = None,
        key: Optional[str] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        clicks: Optional[int] = None,
        target: Optional[str] = None,
        app_path: Optional[str] = None,
        filename: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        try:
            import pyperclip

            if action == "get_screen_info":
                w, h = pyautogui.size()
                mx, my = pyautogui.position()
                return {
                    "success": True,
                    "resolution": {"width": w, "height": h},
                    "mouse_position": {"x": mx, "y": my},
                    "output": f"Screen resolution: {w}x{h}. Cursor currently at: ({mx}, {my})."
                }

            elif action in ["send_keys", "type", "write"]:
                content = text or kwargs.get("content") or kwargs.get("keys") or ""
                if not content:
                    return {"success": False, "output": "Please specify 'text' to type."}
                pyautogui.write(content, interval=0.02)
                return {
                    "success": True,
                    "output": f"Typed text: '{content}' into active desktop focus.",
                    "text": content
                }

            elif action in ["hotkey", "shortcut"]:
                combo_str = keys or key or text or kwargs.get("combo") or "ctrl+c"
                parts = [k.strip().lower() for k in combo_str.replace("-", "+").split("+")]
                pyautogui.hotkey(*parts)
                time.sleep(0.3)
                return {
                    "success": True,
                    "output": f"Executed keyboard shortcut: {' + '.join(parts)}.",
                    "hotkey": parts
                }

            elif action in ["press_key", "enter", "press_enter"]:
                target_key = key or kwargs.get("k") or ("enter" if action in ["enter", "press_enter"] else "enter")
                pyautogui.press(target_key)
                return {
                    "success": True,
                    "output": f"Pressed key '{target_key}'.",
                    "key": target_key
                }

            elif action == "click_screen":
                if x is not None and y is not None:
                    pyautogui.click(x=x, y=y)
                    pos_str = f"({x}, {y})"
                else:
                    pyautogui.click()
                    mx, my = pyautogui.position()
                    pos_str = f"current position ({mx}, {my})"
                return {
                    "success": True,
                    "output": f"Clicked mouse at {pos_str}.",
                    "coordinates": {"x": x, "y": y}
                }

            elif action in ["right_click", "context_menu"]:
                if x is not None and y is not None:
                    pyautogui.rightClick(x=x, y=y)
                    pos_str = f"({x}, {y})"
                else:
                    pyautogui.rightClick()
                    mx, my = pyautogui.position()
                    pos_str = f"current position ({mx}, {my})"
                return {
                    "success": True,
                    "output": f"Right-clicked mouse at {pos_str}."
                }

            elif action == "double_click":
                if x is not None and y is not None:
                    pyautogui.doubleClick(x=x, y=y)
                    pos_str = f"({x}, {y})"
                else:
                    pyautogui.doubleClick()
                    mx, my = pyautogui.position()
                    pos_str = f"current position ({mx}, {my})"
                return {
                    "success": True,
                    "output": f"Double-clicked mouse at {pos_str}."
                }

            elif action in ["move_to", "mouse_move"]:
                if x is None or y is None:
                    return {"success": False, "output": "Please specify both 'x' and 'y' coordinates to move cursor."}
                pyautogui.moveTo(x=x, y=y, duration=0.2)
                return {
                    "success": True,
                    "output": f"Moved mouse cursor to ({x}, {y})."
                }

            elif action in ["drag_to", "mouse_drag"]:
                if x is None or y is None:
                    return {"success": False, "output": "Please specify both 'x' and 'y' target coordinates to drag."}
                pyautogui.dragTo(x=x, y=y, duration=0.3)
                return {
                    "success": True,
                    "output": f"Dragged mouse cursor to ({x}, {y})."
                }

            elif action in ["scroll", "mouse_scroll"]:
                amount = int(clicks if clicks is not None else kwargs.get("amount", -500))
                pyautogui.scroll(amount)
                dir_str = "up" if amount > 0 else "down"
                return {
                    "success": True,
                    "output": f"Scrolled mouse wheel {dir_str} ({amount} clicks)."
                }

            elif action in ["clipboard_copy", "copy_to_clipboard"]:
                content = text or kwargs.get("content") or ""
                if not content:
                    return {"success": False, "output": "Please specify 'text' to copy to clipboard."}
                pyperclip.copy(content)
                return {
                    "success": True,
                    "output": f"Copied {len(content)} characters to Windows clipboard.",
                    "copied_text": content[:100]
                }

            elif action in ["clipboard_paste", "get_clipboard", "read_clipboard"]:
                clip_text = pyperclip.paste()
                return {
                    "success": True,
                    "output": f"Windows Clipboard Content ({len(clip_text)} characters):\n\n{clip_text}",
                    "clipboard": clip_text
                }

            elif action in ["list_windows", "get_windows"]:
                import subprocess, csv, io
                res = subprocess.run("tasklist /v /fo csv", shell=True, capture_output=True, text=True)
                reader = csv.DictReader(io.StringIO(res.stdout))
                active_windows = []
                for row in reader:
                    t = (row.get("Window Title") or "").strip()
                    img = (row.get("Image Name") or "").strip()
                    pid = (row.get("PID") or "").strip()
                    if t and t != "N/A" and not t.startswith("DWM Notification") and not t.startswith("OleMainThread"):
                        active_windows.append({"title": t, "process": img, "pid": pid})
                summary = "\n".join(f"- [{w['process']}] '{w['title']}' (PID: {w['pid']})" for w in active_windows[:20])
                return {
                    "success": True,
                    "windows": active_windows[:25],
                    "output": f"Active Windows on Desktop ({len(active_windows)}):\n\n{summary}"
                }

            elif action in ["focus_window", "activate_window"]:
                win_name = target or text or kwargs.get("name") or ""
                if not win_name:
                    return {"success": False, "output": "Please specify window title or application 'target' to focus."}
                import subprocess
                ps_cmd = f"(New-Object -ComObject WScript.Shell).AppActivate('{win_name}')"
                res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
                activated = "true" in res.stdout.lower()
                time.sleep(0.5)
                return {
                    "success": True,
                    "activated": activated,
                    "output": f"Brought window matching '{win_name}' to foreground."
                }

            elif action == "start_app":
                app_target = app_path or kwargs.get("target") or "notepad.exe"
                if HAS_PYWINAUTO:
                    try:
                        app = pywinauto.Application(backend="win32").start(app_target)
                        time.sleep(1.0)
                        return {
                            "success": True,
                            "output": f"Successfully launched native Windows application '{app_target}' (PID: {app.process}).",
                            "pid": app.process
                        }
                    except Exception:
                        pass
                import subprocess
                p = subprocess.Popen(app_target, shell=True)
                time.sleep(1.0)
                return {
                    "success": True,
                    "output": f"Successfully launched application '{app_target}' (PID: {p.pid}).",
                    "pid": p.pid
                }

            elif action == "take_screenshot":
                screenshots_dir = Path("screenshots")
                screenshots_dir.mkdir(parents=True, exist_ok=True)
                fn = filename or f"screenshot_{int(time.time())}.png"
                out_path = screenshots_dir / fn
                try:
                    pyautogui.screenshot(str(out_path))
                except Exception:
                    time.sleep(0.5)
                    try:
                        pyautogui.screenshot(str(out_path))
                    except Exception as sc_retry_err:
                        return {
                            "success": False,
                            "output": f"Screen grab failed (modal dialog or system window may be blocking capture): {sc_retry_err}"
                        }
                return {
                    "success": True,
                    "output": f"Desktop screenshot saved to '{out_path.resolve()}'.",
                    "file_path": str(out_path.resolve())
                }

            else:
                return {
                    "success": False,
                    "output": f"Unknown desktop GUI action: '{action}'. Available: send_keys, hotkey, press_key, click_screen, right_click, double_click, move_to, drag_to, scroll, clipboard_copy, clipboard_paste, list_windows, focus_window, get_screen_info, start_app, take_screenshot."
                }

        except Exception as e:
            logger.error(f"DesktopGUIControlTool error: {e}", exc_info=True)
            return {
                "success": False,
                "output": f"Desktop GUI control error: {str(e)}",
                "error": str(e)
            }


# Backwards compatibility alias
DesktopGUITool = DesktopGUIControlTool
