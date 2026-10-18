"""Persistent App Memory Store for Helper-AI.

Saves reverse-engineered application profiles, UI automation maps, keyboard shortcuts,
IPC endpoints, and fast-paths so that the agent can operate any PC or web app
with 100% accuracy and maximum speed without rediscovery latency.
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("AppMemoryStore")

MEMORY_ROOT = Path("agent_memory") / "apps"
MARKDOWN_MEMORY_FILE = Path("agent_memory.md")


class AppMemoryStore:
    """Manages persistent AI-friendly application knowledge and fast-paths."""

    _instance: Optional["AppMemoryStore"] = None

    @classmethod
    def get_instance(cls) -> "AppMemoryStore":
        if cls._instance is None:
            cls._instance = AppMemoryStore()
        return cls._instance

    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = Path(memory_dir or MEMORY_ROOT)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_all()
        self._seed_default_apps_if_empty()

    def _slugify(self, text: str) -> str:
        s = text.lower().strip()
        s = re.sub(r'[^\w\s-]', '', s)
        s = re.sub(r'[\s_-]+', '_', s)
        return s or "app"

    def _load_all(self):
        """Loads all stored app profiles from disk."""
        self._cache.clear()
        for p in self.memory_dir.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    slug = data.get("app_slug", p.stem)
                    self._cache[slug] = data
            except Exception as e:
                logger.warning(f"Failed to load app memory from {p}: {e}")

    def save_app_profile(self, profile: Any, data: Optional[Dict[str, Any]] = None, sync_markdown: bool = True) -> Dict[str, Any]:
        """
        Saves or updates an app memory profile to disk and in-memory cache.
        Supports both save_app_profile(dict) and save_app_profile(slug, dict).
        """
        if isinstance(profile, str) and isinstance(data, dict):
            profile_dict = dict(data)
            profile_dict["app_slug"] = profile
        elif isinstance(profile, dict):
            profile_dict = dict(profile)
        else:
            return {"success": False, "error": "Invalid profile format; expected dict or (slug, dict)."}

        app_name = profile_dict.get("app_name") or profile_dict.get("process_name") or "Application"
        slug = profile_dict.get("app_slug") or self._slugify(app_name)
        profile_dict["app_slug"] = slug
        profile_dict["app_name"] = app_name
        profile_dict["last_updated"] = datetime.now().isoformat()
        profile = profile_dict
        
        # Ensure fast_path structure exists
        if "fast_path" not in profile:
            profile["fast_path"] = {}
        if "keyboard_shortcuts" not in profile["fast_path"]:
            profile["fast_path"]["keyboard_shortcuts"] = {}
        if "ui_controls" not in profile["fast_path"]:
            profile["fast_path"]["ui_controls"] = []

        file_path = self.memory_dir / f"{slug}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            self._cache[slug] = profile
            logger.info(f"Saved app memory profile for '{slug}' to {file_path}")

            if sync_markdown:
                self._append_to_markdown_memory(profile)

            return {"success": True, "app_slug": slug, "file_path": str(file_path)}
        except Exception as e:
            logger.error(f"Failed to save app memory for {slug}: {e}")
            return {"success": False, "error": str(e)}

    def get_app_profile(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves an app profile by slug, app_name, process_name, or window title match.
        """
        if not identifier:
            return None
        clean_id = identifier.strip().lower()

        # 1. Direct slug match
        if clean_id in self._cache:
            return self._cache[clean_id]

        slug_candidate = self._slugify(clean_id)
        if slug_candidate in self._cache:
            return self._cache[slug_candidate]

        # 2. Match by process_name, app_name, or window_matchers
        for slug, prof in self._cache.items():
            p_name = str(prof.get("process_name", "")).lower()
            a_name = str(prof.get("app_name", "")).lower()
            if clean_id == p_name or clean_id == a_name:
                return prof
            if clean_id.endswith(".exe") and p_name == clean_id:
                return prof
            if clean_id in a_name or a_name in clean_id:
                return prof
            for matcher in prof.get("window_matchers", []):
                if matcher.lower() in clean_id or clean_id in matcher.lower():
                    return prof

        return None

    def find_matching_profile_for_goal(self, goal_text: str) -> Optional[Dict[str, Any]]:
        """
        Analyzes goal text to find if any remembered application is targeted.
        """
        if not goal_text:
            return None
        lower_goal = goal_text.lower()

        for slug, prof in self._cache.items():
            a_name = str(prof.get("app_name", "")).lower()
            p_name = str(prof.get("process_name", "")).lower().replace(".exe", "")
            slug_key = slug.replace("_", " ")

            patterns = [
                rf"\b{re.escape(a_name)}\b",
                rf"\b{re.escape(p_name)}\b",
                rf"\b{re.escape(slug_key)}\b"
            ]
            for pat in patterns:
                if re.search(pat, lower_goal):
                    return prof

        return None

    def list_all_profiles(self) -> List[Dict[str, Any]]:
        """Returns a summary list of all remembered applications."""
        summaries = []
        for slug, prof in self._cache.items():
            summaries.append({
                "app_slug": slug,
                "app_name": prof.get("app_name", slug),
                "process_name": prof.get("process_name", ""),
                "app_type": prof.get("app_type", "unknown"),
                "launch_command": prof.get("fast_path", {}).get("launch_command", ""),
                "shortcuts_count": len(prof.get("fast_path", {}).get("keyboard_shortcuts", {})),
                "controls_count": len(prof.get("fast_path", {}).get("ui_controls", [])),
                "last_updated": prof.get("last_updated", "")
            })
        return summaries

    def delete_profile(self, slug: str) -> bool:
        """Deletes an app profile from memory."""
        file_path = self.memory_dir / f"{slug}.json"
        if file_path.exists():
            try:
                file_path.unlink()
                self._cache.pop(slug, None)
                return True
            except Exception as e:
                logger.error(f"Failed to delete {slug}: {e}")
                return False
        return False

    def format_for_ai_prompt(self, profile: Dict[str, Any]) -> str:
        """
        Generates a concise, high-density instruction block for the agent LLM.
        """
        name = profile.get("app_name", "App")
        app_type = profile.get("app_type", "native")
        proc = profile.get("process_name", "")
        launch = profile.get("fast_path", {}).get("launch_command", "")
        shortcuts = profile.get("fast_path", {}).get("keyboard_shortcuts", {})
        controls = profile.get("fast_path", {}).get("ui_controls", [])[:10]
        insights = profile.get("reverse_engineering_summary", "")

        lines = [
            f"⚡ KNOWN APP MEMORY AVAILABLE: [{name}] (Type: {app_type}, Process: {proc})",
            f"  - Fast Launch: `{launch}`" if launch else "",
            f"  - Keyboard Hotkeys (100% Fast & Reliable):"
        ]
        for act, key in shortcuts.items():
            lines.append(f"    * {act}: `{key}`")

        if controls:
            lines.append("  - Key UI Controls (Direct Automation):")
            for c in controls:
                c_name = c.get("name") or c.get("automation_id")
                c_type = c.get("type", "Control")
                c_id = c.get("automation_id", "")
                lines.append(f"    * [{c_type}] '{c_name}' (AutomationId: '{c_id}')")

        if insights:
            lines.append(f"  - Operational Insights: {insights[:250]}")

        lines.append("  💡 USE DIRECT FAST-PATHS: Use `fast_app_operate` or `desktop_gui_control` with the hotkeys/controls above to achieve the goal in 1 step without exploratory delays!")
        return "\n".join([line for line in lines if line])

    def _append_to_markdown_memory(self, profile: Dict[str, Any]):
        """Appends a human-readable reverse engineering record to agent_memory.md."""
        try:
            slug = profile.get("app_slug", "app")
            name = profile.get("app_name", slug)
            proc = profile.get("process_name", "")
            app_type = profile.get("app_type", "native")
            shortcuts = profile.get("fast_path", {}).get("keyboard_shortcuts", {})

            md_entry = (
                f"\n\n---\n\n"
                f"## 🧩 Reverse-Engineered App Memory: {name} (`{slug}`)\n\n"
                f"- **Process Name:** `{proc}`\n"
                f"- **Application Type:** `{app_type}`\n"
                f"- **Discovered Hotkeys:** {len(shortcuts)} shortcuts\n"
            )
            if shortcuts:
                md_entry += "- **Fast Shortcuts:**\n"
                for act, key in list(shortcuts.items())[:8]:
                    md_entry += f"  - `{act}`: `{key}`\n"

            summary = profile.get("reverse_engineering_summary", "")
            if summary:
                md_entry += f"- **Architecture Summary:** {summary}\n"

            with open(MARKDOWN_MEMORY_FILE, "a", encoding="utf-8") as f:
                f.write(md_entry)
        except Exception as e:
            logger.warning(f"Could not append to agent_memory.md: {e}")

    def _seed_default_apps_if_empty(self):
        """Pre-seeds standard foundational Windows and Web applications."""
        if len(self._cache) > 0:
            return

        defaults = [
            {
                "app_name": "Notepad",
                "app_slug": "notepad",
                "process_name": "notepad.exe",
                "app_type": "native_win32",
                "window_matchers": ["Notepad", "Untitled - Notepad"],
                "reverse_engineering_summary": "Standard Windows text editor. Has Edit control (AutomationId 15) and Menu bar. Direct hotkeys allow instant document operations.",
                "fast_path": {
                    "launch_command": "notepad",
                    "keyboard_shortcuts": {
                        "save": "ctrl+s",
                        "save_as": "ctrl+shift+s",
                        "open": "ctrl+o",
                        "new": "ctrl+n",
                        "find": "ctrl+f",
                        "replace": "ctrl+h",
                        "select_all": "ctrl+a",
                        "exit": "alt+f4"
                    },
                    "ui_controls": [
                        {"name": "Text Editor", "type": "Edit", "automation_id": "15"},
                        {"name": "File", "type": "MenuItem", "automation_id": "Item 1"},
                        {"name": "Edit", "type": "MenuItem", "automation_id": "Item 2"}
                    ]
                }
            },
            {
                "app_name": "Calculator",
                "app_slug": "calculator",
                "process_name": "CalculatorApp.exe",
                "app_type": "wpf_winui",
                "window_matchers": ["Calculator"],
                "reverse_engineering_summary": "Windows UWP/WinUI Calculator. Keyboard digits and operators work directly via hotkey/send_keys. AutomationIds map directly to buttons.",
                "fast_path": {
                    "launch_command": "calc",
                    "keyboard_shortcuts": {
                        "clear": "esc",
                        "equals": "enter",
                        "add": "+",
                        "subtract": "-",
                        "multiply": "*",
                        "divide": "/"
                    },
                    "ui_controls": [
                        {"name": "Display", "type": "Text", "automation_id": "CalculatorResults"},
                        {"name": "Clear", "type": "Button", "automation_id": "clearButton"},
                        {"name": "Equals", "type": "Button", "automation_id": "equalButton"}
                    ]
                }
            },
            {
                "app_name": "Visual Studio Code",
                "app_slug": "vscode",
                "process_name": "Code.exe",
                "app_type": "electron",
                "window_matchers": ["Visual Studio Code"],
                "reverse_engineering_summary": "Electron code editor. IPC channels handle window and workbench actions. Command palette is fastest entrypoint for any action.",
                "fast_path": {
                    "launch_command": "code",
                    "keyboard_shortcuts": {
                        "command_palette": "ctrl+shift+p",
                        "quick_open": "ctrl+p",
                        "save": "ctrl+s",
                        "toggle_terminal": "ctrl+`",
                        "find": "ctrl+f",
                        "close_editor": "ctrl+w",
                        "split_editor": "ctrl+\\"
                    },
                    "ui_controls": []
                }
            },
            {
                "app_name": "Google Chrome",
                "app_slug": "chrome",
                "process_name": "chrome.exe",
                "app_type": "web_browser",
                "window_matchers": ["Google Chrome"],
                "reverse_engineering_summary": "Chromium multi-process browser. Address bar focused instantly via Ctrl+L. Tabs operated directly via hotkeys.",
                "fast_path": {
                    "launch_command": "start chrome",
                    "keyboard_shortcuts": {
                        "focus_address_bar": "ctrl+l",
                        "new_tab": "ctrl+t",
                        "close_tab": "ctrl+w",
                        "reopen_closed_tab": "ctrl+shift+t",
                        "reload": "ctrl+r",
                        "downloads": "ctrl+j",
                        "history": "ctrl+h",
                        "incognito": "ctrl+shift+n"
                    },
                    "ui_controls": []
                }
            },
            {
                "app_name": "Microsoft Edge",
                "app_slug": "edge",
                "process_name": "msedge.exe",
                "app_type": "web_browser",
                "window_matchers": ["Microsoft Edge"],
                "reverse_engineering_summary": "Windows default Chromium browser. Address bar (Ctrl+L), DevTools (F12), Tabs (Ctrl+T/Ctrl+W).",
                "fast_path": {
                    "launch_command": "start msedge",
                    "keyboard_shortcuts": {
                        "focus_address_bar": "ctrl+l",
                        "new_tab": "ctrl+t",
                        "close_tab": "ctrl+w",
                        "reload": "ctrl+r",
                        "favorites": "ctrl+shift+o"
                    },
                    "ui_controls": []
                }
            },
            {
                "app_name": "File Explorer",
                "app_slug": "file_explorer",
                "process_name": "explorer.exe",
                "app_type": "native_win32",
                "window_matchers": ["File Explorer", "This PC"],
                "reverse_engineering_summary": "Windows Shell File Manager. Alt+D focuses the address bar instantly to paste or type paths. Ctrl+Shift+N creates new folder.",
                "fast_path": {
                    "launch_command": "explorer",
                    "keyboard_shortcuts": {
                        "focus_address_bar": "alt+d",
                        "new_folder": "ctrl+shift+n",
                        "rename": "f2",
                        "search": "ctrl+e",
                        "new_window": "ctrl+n",
                        "properties": "alt+enter"
                    },
                    "ui_controls": []
                }
            }
        ]

        for app in defaults:
            self.save_app_profile(app, sync_markdown=False)
