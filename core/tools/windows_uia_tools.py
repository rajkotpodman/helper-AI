"""Windows UI Automation (UIA) Native Desktop Automation Tool (Microsoft UFO Pattern).

Enables deterministic, coordinate-free desktop automation by interacting directly
with the Windows UI Automation (UIA) accessibility tree. Allows the AI agent to
list open windows, find and click buttons by name ("Save", "OK", "Cancel", "File"),
type text into input fields, and select menus with 100% precision.
"""

import os
import sys
import time
import logging
from typing import Dict, Any, List, Optional
from core.tools.base import BaseTool

logger = logging.getLogger("WindowsUIATool")

# Safe imports for Windows UI Automation
UIAUTOMATION_AVAILABLE = False
PYWINAUTO_AVAILABLE = False

try:
    if sys.platform == "win32":
        import uiautomation as uia
        UIAUTOMATION_AVAILABLE = True
except Exception as e:
    logger.debug(f"uiautomation import failed: {e}")

try:
    if sys.platform == "win32":
        from pywinauto import Desktop, Application
        PYWINAUTO_AVAILABLE = True
except Exception as e:
    logger.debug(f"pywinauto import failed: {e}")


class WindowsUIATool(BaseTool):
    """Native Windows UI Automation Tool inspired by Microsoft UFO."""

    name = "windows_uia"
    description = (
        "Controls Windows desktop software using the native UI Automation (UIA) tree. "
        "Directly finds and clicks buttons ('Save', 'OK', 'Cancel', 'Submit', 'File'), "
        "types text into input fields by name/placeholder, selects menu items ('File -> Save As'), "
        "inspects interactive window controls, lists open desktop windows, and focuses applications "
        "with 100% precision without relying on screen coordinates."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "list_windows",
                    "inspect_window",
                    "click_control",
                    "type_control",
                    "select_menu",
                    "focus_window",
                    "close_window"
                ],
                "default": "list_windows",
                "description": (
                    "Action to perform: 'list_windows' (show open apps), "
                    "'inspect_window' (list buttons and fields in a window), "
                    "'click_control' (click button by visible name), "
                    "'type_control' (type text into an input box by name), "
                    "'select_menu' (select menu path like 'File -> Save As'), "
                    "'focus_window' (bring window to foreground), "
                    "'close_window' (close application window)."
                )
            },
            "window_title": {
                "type": "string",
                "description": "Title or partial name of target application window (e.g. 'Notepad', 'Excel', 'Chrome')."
            },
            "control_name": {
                "type": "string",
                "description": "Name or text of control to interact with (e.g. 'Save', 'OK', 'Cancel', 'File', 'Username')."
            },
            "control_type": {
                "type": "string",
                "enum": ["Button", "Edit", "MenuItem", "CheckBox", "RadioButton", "TabItem", "ComboBox", "Hyperlink", "Any"],
                "default": "Any",
                "description": "Control type filter (e.g. 'Button', 'Edit', 'MenuItem', 'Any')."
            },
            "text": {
                "type": "string",
                "description": "Text to type into the field (for action='type_control')."
            },
            "menu_path": {
                "type": "string",
                "description": "Menu navigation path separated by '->' (e.g. 'File -> Save As' or 'Edit -> Preferences')."
            },
            "press_enter": {
                "type": "boolean",
                "default": False,
                "description": "Whether to press Enter after typing text."
            },
            "max_depth": {
                "type": "integer",
                "default": 3,
                "description": "Maximum tree search depth for inspecting window elements (default: 3)."
            }
        },
        "required": ["action"]
    }

    def execute(
        self,
        action: str = "list_windows",
        window_title: Optional[str] = None,
        control_name: Optional[str] = None,
        control_type: str = "Any",
        text: Optional[str] = None,
        menu_path: Optional[str] = None,
        press_enter: bool = False,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        if sys.platform != "win32":
            return {
                "success": False,
                "error": "Windows UI Automation (UIA) is only supported on Windows operating systems.",
                "action": action
            }

        if not UIAUTOMATION_AVAILABLE and not PYWINAUTO_AVAILABLE:
            return {
                "success": False,
                "error": "Neither 'uiautomation' nor 'pywinauto' library is available. Run: pip install uiautomation pywinauto",
                "action": action
            }

        try:
            if action == "list_windows":
                return self._list_windows()
            elif action == "inspect_window":
                return self._inspect_window(window_title, max_depth)
            elif action == "click_control":
                if not control_name:
                    return {"success": False, "error": "control_name is required for action='click_control'."}
                return self._click_control(window_title, control_name, control_type)
            elif action == "type_control":
                if not control_name:
                    return {"success": False, "error": "control_name is required for action='type_control'."}
                if text is None:
                    return {"success": False, "error": "text is required for action='type_control'."}
                return self._type_control(window_title, control_name, text, press_enter)
            elif action == "select_menu":
                if not menu_path:
                    return {"success": False, "error": "menu_path is required for action='select_menu'."}
                return self._select_menu(window_title, menu_path)
            elif action == "focus_window":
                return self._focus_window(window_title)
            elif action == "close_window":
                return self._close_window(window_title)
            else:
                return {"success": False, "error": f"Unknown action: '{action}'"}
        except Exception as e:
            logger.error(f"Error executing WindowsUIATool action '{action}': {e}", exc_info=True)
            return {
                "success": False,
                "action": action,
                "error": str(e)
            }

    # -------------------------------------------------------------------------
    # Core Implementation Methods
    # -------------------------------------------------------------------------

    def _get_target_window(self, title_pattern: Optional[str] = None):
        """Finds a top-level window by title substring or returns the current active window."""
        if UIAUTOMATION_AVAILABLE:
            root = uia.GetRootControl()
            if title_pattern:
                title_lower = title_pattern.lower()
                for child in root.GetChildren():
                    if child.Name and title_lower in child.Name.lower():
                        return child
            else:
                # Return focused control's top-level window or first non-empty window
                focused = uia.GetFocusedControl()
                if focused:
                    curr = focused
                    while curr and curr.GetParentControl() and curr.GetParentControl() != root:
                        curr = curr.GetParentControl()
                    if curr and curr.Name:
                        return curr
                # Fallback to first non-desktop top level window
                for child in root.GetChildren():
                    if child.Name and child.ClassName not in ["Shell_TrayWnd", "Progman", "WorkerW"]:
                        return child
        return None

    def _list_windows(self) -> Dict[str, Any]:
        """Lists all visible top-level windows."""
        windows = []
        if UIAUTOMATION_AVAILABLE:
            root = uia.GetRootControl()
            for child in root.GetChildren():
                name = child.Name
                class_name = child.ClassName
                if name and class_name not in ["Progman", "WorkerW"]:
                    rect = child.BoundingRectangle
                    windows.append({
                        "title": name,
                        "class_name": class_name,
                        "process_id": getattr(child, "ProcessId", None),
                        "bounding_box": {
                            "left": rect.left,
                            "top": rect.top,
                            "right": rect.right,
                            "bottom": rect.bottom,
                            "width": rect.width(),
                            "height": rect.height()
                        } if rect else None
                    })

        return {
            "success": True,
            "window_count": len(windows),
            "windows": windows
        }

    def _inspect_window(self, window_title: Optional[str] = None, max_depth: int = 3) -> Dict[str, Any]:
        """Inspects all clickable and editable controls inside a window."""
        target_win = self._get_target_window(window_title)
        if not target_win:
            return {
                "success": False,
                "error": f"Window '{window_title}' not found. Use action='list_windows' to view open windows."
            }

        controls = []
        if UIAUTOMATION_AVAILABLE:
            for ctrl, depth in uia.WalkControl(target_win, maxDepth=max_depth):
                # We care about interactive elements: Button, Edit, MenuItem, CheckBox, TabItem, Hyperlink, etc.
                ctype = ctrl.ControlTypeName
                name = ctrl.Name
                auto_id = ctrl.AutomationId

                if name or auto_id or ctype in ["ButtonControl", "EditControl", "MenuItemControl"]:
                    rect = ctrl.BoundingRectangle
                    controls.append({
                        "name": name,
                        "control_type": ctype.replace("Control", ""),
                        "automation_id": auto_id,
                        "is_enabled": getattr(ctrl, "IsEnabled", True),
                        "depth": depth,
                        "bounding_box": {
                            "left": rect.left,
                            "top": rect.top,
                            "width": rect.width(),
                            "height": rect.height()
                        } if rect else None
                    })

        return {
            "success": True,
            "window_title": target_win.Name,
            "control_count": len(controls),
            "controls": controls[:100]  # Cap at 100 for token efficiency
        }

    def _click_control(
        self,
        window_title: Optional[str],
        control_name: str,
        control_type: str = "Any"
    ) -> Dict[str, Any]:
        """Finds and clicks a control by name using native UIA Invoke or Click."""
        target_win = self._get_target_window(window_title)
        if not target_win:
            return {"success": False, "error": f"Window '{window_title}' not found."}

        target_win.SetActive()
        time.sleep(0.2)

        name_lower = control_name.lower()
        matched_ctrl = None

        if UIAUTOMATION_AVAILABLE:
            for ctrl, _ in uia.WalkControl(target_win, maxDepth=5):
                c_name = (ctrl.Name or "").lower()
                c_id = (ctrl.AutomationId or "").lower()
                c_type = ctrl.ControlTypeName.replace("Control", "")

                # Type check
                if control_type != "Any" and c_type.lower() != control_type.lower():
                    continue

                # Name match (exact or substring)
                if c_name == name_lower or c_id == name_lower or name_lower in c_name:
                    matched_ctrl = ctrl
                    break

        if not matched_ctrl:
            return {
                "success": False,
                "error": f"Control with name '{control_name}' (type={control_type}) not found in window '{target_win.Name}'."
            }

        # Try native InvokePattern first, then Click
        try:
            pattern = matched_ctrl.GetInvokePattern()
            if pattern:
                pattern.Invoke()
                return {
                    "success": True,
                    "action": "invoked",
                    "control_name": matched_ctrl.Name,
                    "control_type": matched_ctrl.ControlTypeName,
                    "window": target_win.Name
                }
        except Exception:
            pass

        # Try Click directly
        try:
            matched_ctrl.Click(simulateMove=False)
            return {
                "success": True,
                "action": "clicked",
                "control_name": matched_ctrl.Name,
                "control_type": matched_ctrl.ControlTypeName,
                "window": target_win.Name
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Found control '{matched_ctrl.Name}' but failed to click: {e}"
            }

    def _type_control(
        self,
        window_title: Optional[str],
        control_name: str,
        text: str,
        press_enter: bool = False
    ) -> Dict[str, Any]:
        """Finds an Edit/Input control and sets text value."""
        target_win = self._get_target_window(window_title)
        if not target_win:
            return {"success": False, "error": f"Window '{window_title}' not found."}

        target_win.SetActive()
        time.sleep(0.2)

        name_lower = control_name.lower()
        matched_ctrl = None

        if UIAUTOMATION_AVAILABLE:
            for ctrl, _ in uia.WalkControl(target_win, maxDepth=5):
                c_name = (ctrl.Name or "").lower()
                c_id = (ctrl.AutomationId or "").lower()
                c_type = ctrl.ControlTypeName

                if "Edit" in c_type or "Document" in c_type:
                    if not control_name or name_lower in c_name or name_lower in c_id:
                        matched_ctrl = ctrl
                        break

        if not matched_ctrl:
            return {
                "success": False,
                "error": f"Edit control '{control_name}' not found in window '{target_win.Name}'."
            }

        try:
            # Set focus
            matched_ctrl.SetFocus()
            # Try ValuePattern
            try:
                vp = matched_ctrl.GetValuePattern()
                if vp:
                    vp.SetValue(text)
                else:
                    matched_ctrl.SendKeys(text)
            except Exception:
                matched_ctrl.SendKeys(text)

            if press_enter:
                matched_ctrl.SendKeys("{Enter}")

            return {
                "success": True,
                "control_name": matched_ctrl.Name,
                "text_typed": text,
                "window": target_win.Name
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to type into '{matched_ctrl.Name}': {e}"
            }

    def _select_menu(self, window_title: Optional[str], menu_path: str) -> Dict[str, Any]:
        """Selects a menu item path like 'File -> Save As'."""
        target_win = self._get_target_window(window_title)
        if not target_win:
            return {"success": False, "error": f"Window '{window_title}' not found."}

        target_win.SetActive()
        time.sleep(0.2)

        parts = [p.strip() for p in menu_path.split("->")]
        for part in parts:
            res = self._click_control(window_title=target_win.Name, control_name=part, control_type="MenuItem")
            if not res["success"]:
                # Try Any control type
                res = self._click_control(window_title=target_win.Name, control_name=part, control_type="Any")
                if not res["success"]:
                    return {"success": False, "error": f"Failed navigating menu item '{part}' in path '{menu_path}': {res.get('error')}"}
            time.sleep(0.3)

        return {
            "success": True,
            "menu_path": menu_path,
            "window": target_win.Name
        }

    def _focus_window(self, window_title: Optional[str]) -> Dict[str, Any]:
        """Brings the window to foreground."""
        target_win = self._get_target_window(window_title)
        if not target_win:
            return {"success": False, "error": f"Window '{window_title}' not found."}

        target_win.SetActive()
        return {"success": True, "window_title": target_win.Name}

    def _close_window(self, window_title: Optional[str]) -> Dict[str, Any]:
        """Closes the specified application window."""
        target_win = self._get_target_window(window_title)
        if not target_win:
            return {"success": False, "error": f"Window '{window_title}' not found."}

        try:
            # Try WindowPattern close
            wp = target_win.GetWindowPattern()
            if wp:
                wp.Close()
                return {"success": True, "message": f"Window '{target_win.Name}' closed."}
        except Exception:
            pass

        # Try Alt+F4
        target_win.SetActive()
        target_win.SendKeys("{Alt}{F4}")
        return {"success": True, "message": f"Sent Alt+F4 to '{target_win.Name}'."}
