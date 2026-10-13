"""Dynamic Command Downloader and Community Knowledge Fetcher.

Downloads, caches, and retrieves cheatsheets, usage manuals, and specialized
recipes for any terminal command or CLI utility across all operating systems.
"""

import os
import re
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from core.command_engine.command_encyclopedia import CommandEncyclopedia


class CommandFetcher:
    """Downloads and caches terminal command cheat sheets and recipes from community hubs."""

    CACHE_DIR = Path.home() / ".helper_ai" / "command_cache"
    DEFAULT_TIMEOUT = 5.0

    @classmethod
    def _get_cache_path(cls, topic: str) -> Path:
        """Returns the local cache file path for a command."""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', topic.lower().strip())
        return cls.CACHE_DIR / f"{safe_name}.txt"

    @classmethod
    def fetch_command_cheatsheet(cls, command_or_tool: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Retrieves comprehensive usage guidelines and recipes for a command.
        Checks local cache first, queries online community repositories,
        and falls back to built-in encyclopedic knowledge.

        Args:
            command_or_tool: Name of the command (e.g. 'tar', 'ffmpeg', 'docker', 'powershell', 'iptables').
            force_refresh: Whether to bypass cache and fetch fresh from web.

        Returns:
            Dictionary with source ('cache', 'online', 'encyclopedia'), command, and content.
        """
        tool_clean = command_or_tool.strip().lower()
        cache_file = cls._get_cache_path(tool_clean)

        # 1. Check local persistent cache
        if cache_file.exists() and not force_refresh:
            try:
                content = cache_file.read_text(encoding="utf-8")
                if content.strip():
                    return {
                        "success": True,
                        "source": "cache",
                        "topic": tool_clean,
                        "content": content
                    }
            except Exception:
                pass

        # 2. Attempt online download from cheat.sh / community APIs
        online_content = cls._download_from_cheat_sh(tool_clean)
        if online_content:
            try:
                cache_file.write_text(online_content, encoding="utf-8")
            except Exception:
                pass
            return {
                "success": True,
                "source": "online_repository",
                "topic": tool_clean,
                "content": online_content
            }

        # 3. Fallback to built-in encyclopedic search
        encyclopedia_matches = CommandEncyclopedia.search_recipes(tool_clean)
        if encyclopedia_matches:
            formatted_matches = []
            for m in encyclopedia_matches:
                formatted_matches.append(
                    f"Command: {m['name']}\nDescription: {m['description']}\nWindows: {m['windows_example']}\nPOSIX: {m['posix_example']}\n"
                )
            combined = "\n---\n".join(formatted_matches)
            return {
                "success": True,
                "source": "built_in_encyclopedia",
                "topic": tool_clean,
                "content": combined
            }

        return {
            "success": False,
            "source": "not_found",
            "topic": tool_clean,
            "error": f"No online or offline cheat sheet found for '{command_or_tool}'."
        }

    @classmethod
    def _download_from_cheat_sh(cls, tool_name: str) -> Optional[str]:
        """Downloads clean ASCII cheat sheet from cheat.sh."""
        url = f"https://cheat.sh/{tool_name}?T"
        headers = {
            "User-Agent": "curl/7.88.1 (Helper-AI Universal Command Engine)"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=cls.DEFAULT_TIMEOUT)
            if resp.status_code == 200 and len(resp.text) > 50 and "Unknown topic" not in resp.text:
                # Strip ANSI escape sequences if any
                clean_text = re.sub(r'\x1b\[[0-9;]*m', '', resp.text)
                return clean_text.strip()
        except Exception:
            pass
        return None
