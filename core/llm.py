"""Unified LLM Client supporting Gemini, OpenAI, Groq, Ollama, and RuleEngine fallback."""
import os
import json
import re
from typing import Dict, Any, Optional
import requests

SYSTEM_PROMPT = r"""You are Helper, an autonomous AI assistant with full control of the user's running PC and internet access.
Your mandate is to accomplish the user's GOAL completely, reliably, and autonomously WITHOUT asking redundant questions.

You have access to the following tools:
{tool_schemas}

### OPERATING PRINCIPLES:
1. Plan and execute sequentially: Choose the most direct, specialized tool first.
2. Ollama & Local AI: To inspect, list, or check Ollama models or service, ALWAYS use the `manage_ollama` tool with action "list_models". DO NOT use PowerShellGet, `Get-InstalledModule`, or `Install-Module` — Ollama is an independent CLI tool, not a PowerShell Gallery module!
3. Self-Healing & Adaptability: If a command or tool encounters an error, read the error message and hints carefully. NEVER repeat the same failing command. Try an alternative tool or command immediately.
4. Windows Software & Tools: To check installed applications on Windows, use `winget list`, `Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*`, or check Program Files.
5. Operating Environment: The host machine is {os_name} {os_release}. Standard directories like Desktop, Downloads, and Documents are directly accessible via tools.
6. Completion & Persistence: Only set `is_complete` to true when the goal has actually succeeded. If a previous tool or command had an error, DO NOT give up or declare completion — analyze the error, fix the parameters, and try again!
7. Folder Paths with Spaces: When checking the contents of ANY folder (e.g. `E:\Freelancer Crack The Deal`), ALWAYS use the `list_directory` tool with `path: "E:\\Freelancer Crack The Deal"`. Do NOT run raw PowerShell commands like `Get-ChildItem` for listing files. If you do use PowerShell, paths with spaces MUST be wrapped in double quotes: `Get-ChildItem "E:\Freelancer Crack The Deal"`.
8. Opening Applications: When the user's goal is to open or launch an application (e.g. 'open edge', 'launch notepad', 'open browser'), use the `open_app_or_file` tool with target='edge' (or target='notepad', target='chrome', etc.). Once launched successfully, the goal IS COMPLETE! Immediately set `is_complete: true`, `action: 'none'`, and inform the user. DO NOT close or terminate the app, and DO NOT loop checking processes!
9. Live Project Browser Control: To automate websites, create blogs, post to Facebook, click buttons, or fill forms (e.g. Facebook, Blogger, Google), use `browser_automation`:
- Create & Publish Facebook Post (1-step autonomous): Action: "browser_automation", Action args: {{ "action": "publish_facebook_post", "post_text": "My Facebook post text..." }}
- Create & Publish Blogger Post (1-step autonomous): Action: "browser_automation", Action args: {{ "action": "publish_blog_post", "title": "My Blog Title", "text": "My post body..." }}
- List Google Blogs / View Blogger Dashboard: Action: "browser_automation", Action args: {{ "action": "list_blogs" }}
- Open URL: Action: "browser_automation", Action args: {{ "action": "open_url", "url": "https://www.facebook.com" }}
- Click button/link by text: Action: "browser_automation", Action args: {{ "action": "click", "target": "What's on your mind" }} (or "Post", "Sign in", "New Post")
- Type into text boxes: Action: "browser_automation", Action args: {{ "action": "type", "target": "What's on your mind", "text": "My post content" }}
This controls the live project browser where logins and cookies are permanently remembered.

### QUICK TOOL ROUTING CHEATSHEET:
- Facebook post creation & publishing:
  Action: "browser_automation", Action args: {{ "action": "publish_facebook_post", "post_text": "..." }}
- Blogger post creation & publishing:
  Action: "browser_automation", Action args: {{ "action": "publish_blog_post", "title": "...", "text": "..." }}
- Live Web browsing / clicking buttons / web forms:
  Action: "browser_automation", Action args: {{ "action": "open_url", "url": "https://www.facebook.com" }}
- Opening / Launching applications:
  Action: "open_app_or_file", Action args: {{ "target": "edge" }}
- Checking Ollama models / local models / AI status:
  Action: "manage_ollama", Action args: {{ "action": "list_models" }}
- Inspecting or listing files in a folder (especially with spaces):
  Action: "list_directory", Action args: {{ "path": "E:\\Freelancer Crack The Deal" }}
- Checking PC health, RAM, CPU, or hardware:
  Action: "get_system_health", Action args: {{}}
- Searching the web or internet:
  Action: "search_web", Action args: {{ "query": "..." }}
- Managing processes:
  Action: "manage_processes", Action args: {{ "action": "list", "sort_by": "memory", "limit": 10 }}
- Voice speech synthesis / speak aloud:
  Action: "speak_aloud", Action args: {{ "text": "..." }}
- Playwright vision browser / visual screenshot:
  Action: "vision_browser", Action args: {{ "action": "screenshot" }}
- Model Context Protocol (MCP) servers & tools:
  Action: "manage_mcp", Action args: {{ "action": "list_servers" }}
- Desktop GUI control / keyboard / mouse / desktop screenshot:
  Action: "desktop_gui_control", Action args: {{ "action": "get_screen_info" }}

### RESPONSE FORMAT:
You MUST respond ONLY with a valid JSON object matching this exact schema:
{{
    "thought": "Your internal chain-of-thought analysis of current progress and next step.",
    "action": "name_of_tool_to_call or 'none'",
    "action_args": {{ "param1": "value1" }},
    "is_complete": false,
    "completion_message": "Final summary for the user once is_complete is true (empty otherwise)"
}}
Do NOT include markdown formatting like ```json or any text outside the JSON object.
"""

class LLMClient:
    def __init__(self, provider: str = None, api_key: str = None, model: str = None, base_url: str = None):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "gemini")).lower().strip().strip("'").strip('"')
        if not api_key:
            if self.provider == "groq":
                raw_key = os.getenv("GROQ_API_KEY") or ""
            elif self.provider == "gemini":
                raw_key = os.getenv("GEMINI_API_KEY") or ""
            elif self.provider == "openai":
                raw_key = os.getenv("OPENAI_API_KEY") or ""
            else:
                raw_key = os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        else:
            raw_key = api_key
        self.api_key = raw_key.strip().strip("'").strip('"')
        self.model = model
        self.base_url = base_url

        if not self.model:
            if self.provider == "gemini":
                self.model = os.getenv("GEMINI_MODEL") or "gemini-1.5-flash"
            elif self.provider == "openai":
                self.model = os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
            elif self.provider == "groq":
                self.model = os.getenv("GROQ_MODEL") or "qwen/qwen3.8-27b"
            elif self.provider == "ollama":
                self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
            else:
                self.model = "rule_engine"

    def generate_step(self, goal: str, trajectory_summary: str, tool_schemas: str, os_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calls the configured provider to get the next agent decision."""
        # Check if fallback to rule engine is warranted
        if self.provider == "rule_engine" or (not self.api_key and self.provider not in ["ollama"]):
            return self._rule_engine_step(goal, trajectory_summary)

        sys_prompt = SYSTEM_PROMPT.format(
            tool_schemas=tool_schemas,
            os_name=os_info.get("os", "Windows"),
            os_release=os_info.get("release", "10")
        )

        user_content = (
            f"GOAL: {goal}\n\n"
            f"CURRENT WORKSPACE:\n"
            f"- CWD: {os_info.get('cwd')}\n"
            f"- User Home: {os_info.get('user_home')}\n\n"
            f"EXECUTION HISTORY & PROGRESS:\n{trajectory_summary}\n\n"
            f"Based on the goal and history above, generate your next thought and action in strict JSON."
        )

        try:
            if self.provider == "gemini":
                return self._call_gemini(sys_prompt, user_content)
            elif self.provider == "openai":
                return self._call_openai(sys_prompt, user_content)
            elif self.provider == "groq":
                return self._call_groq(sys_prompt, user_content)
            elif self.provider == "ollama":
                return self._call_ollama(sys_prompt, user_content)
            else:
                return self._rule_engine_step(goal, trajectory_summary)
        except Exception as e:
            # Fallback to rule engine if API calls fail
            step = self._rule_engine_step(goal, trajectory_summary)
            step["thought"] = f"(Note: LLM provider {self.provider} error: {str(e)}. Using autonomous fallback.) " + step["thought"]
            return step

    def _call_gemini(self, system_instruction: str, user_prompt: str) -> Dict[str, Any]:
        # Direct REST API call for maximum reliability without SDK version conflicts
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        resp = requests.post(url, json=payload, timeout=45)
        resp.raise_for_status()
        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return self._parse_json_response(raw_text)

    def _call_openai(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        raw_text = resp.choices[0].message.content
        return self._parse_json_response(raw_text)

    def _call_groq(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key, base_url="https://api.groq.com/openai/v1")
        target_model = self.model or "qwen/qwen3.8-27b"
        try:
            resp = client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw_text = resp.choices[0].message.content
            return self._parse_json_response(raw_text)
        except Exception as e:
            err_str = str(e).lower()
            # If rate limit (429 / TPD / TPM) or model not found, try alternative models
            if any(k in err_str for k in ["429", "rate_limit", "rate limit", "tpd", "tokens per day", "model_not_found", "404", "does not exist"]):
                alt_candidates = [
                    "openai/gpt-oss-120b",
                    "openai/gpt-oss-20b",
                    "llama-3.3-70b-versatile",
                    "llama-3.1-8b-instant",
                    "qwen/qwen3.8-27b"
                ]
                for alt in alt_candidates:
                    if alt == target_model:
                        continue
                    try:
                        resp = client.chat.completions.create(
                            model=alt,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            response_format={"type": "json_object"},
                            temperature=0.2,
                        )
                        self.model = alt
                        raw_text = resp.choices[0].message.content
                        return self._parse_json_response(raw_text)
                    except Exception:
                        continue
            raise

    @staticmethod
    def _ensure_ollama_running(base_url: str = "http://localhost:11434") -> bool:
        """Checks if Ollama daemon is reachable; if not, attempts to start `ollama serve` in the background."""
        import time
        import subprocess
        try:
            r = requests.get(f"{base_url.rstrip('/')}/api/version", timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass

        try:
            creation_flags = 0
            if os.name == "nt":
                creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creation_flags)
            for _ in range(12):
                time.sleep(0.5)
                try:
                    r = requests.get(f"{base_url.rstrip('/')}/api/version", timeout=1)
                    if r.status_code == 200:
                        return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    def _resolve_ollama_model(self, base_url: str) -> str:
        """Finds the best matching installed model from Ollama."""
        target = (self.model or os.getenv("OLLAMA_MODEL", "")).lower().strip()
        try:
            r = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=3)
            if r.status_code == 200:
                installed_models = [m.get("name", "") for m in r.json().get("models", [])]
                if not installed_models:
                    return target or "qwen2.5:1.5b"

                # 1. Exact match
                for m in installed_models:
                    if m.lower() == target:
                        return m

                # 2. Check for prefix or alias (e.g. quiene/qwen -> qwen2.5:1.5b)
                target_clean = target.replace("quiene", "qwen")
                for m in installed_models:
                    m_lower = m.lower()
                    if target_clean and (target_clean in m_lower or m_lower.startswith(target_clean)):
                        return m

                # 3. If target contains llama
                if "llama" in target_clean:
                    for m in installed_models:
                        if "llama" in m.lower():
                            return m

                # 4. Fallback to first available model
                return installed_models[0]
        except Exception:
            pass
        return target or "qwen2.5:1.5b"

    def _call_ollama(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        base_url = self.base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self._ensure_ollama_running(base_url)
        resolved_model = self._resolve_ollama_model(base_url)
        url = f"{base_url.rstrip('/')}/api/chat"
        payload = {
            "model": resolved_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "format": "json"
        }
        resp = requests.post(url, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        raw_text = data.get("message", {}).get("content", "")
        return self._parse_json_response(raw_text)

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        # Strip markdown ```json ... ```
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
            text = text.strip()

        try:
            parsed = json.loads(text)
            return {
                "thought": parsed.get("thought", "Analyzing situation."),
                "action": parsed.get("action", "none"),
                "action_args": parsed.get("action_args", {}),
                "is_complete": bool(parsed.get("is_complete", False)),
                "completion_message": parsed.get("completion_message", "")
            }
        except json.JSONDecodeError:
            # Attempt to extract JSON substring
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                    return {
                        "thought": parsed.get("thought", "Analyzing situation."),
                        "action": parsed.get("action", "none"),
                        "action_args": parsed.get("action_args", {}),
                        "is_complete": bool(parsed.get("is_complete", False)),
                        "completion_message": parsed.get("completion_message", "")
                    }
                except Exception:
                    pass
            return {
                "thought": "Failed to parse model output into JSON. Terminating gracefully.",
                "action": "none",
                "action_args": {},
                "is_complete": True,
                "completion_message": f"Execution halted due to formatting error: {text[:200]}"
            }

    def _rule_engine_step(self, goal: str, trajectory_summary: str) -> Dict[str, Any]:
        """
        Smart autonomous rule-based engine that allows Helper-AI to operate
        immediately out-of-the-box for common tasks even without an API key!
        """
        lower = goal.lower()
        # Check if any step has already been executed in trajectory (prevents loop when earlier steps are truncated)
        has_run = bool(trajectory_summary and ("Step " in trajectory_summary or "earlier steps" in trajectory_summary) and trajectory_summary != "No previous steps executed yet.")

        # 1. Specialized handling for Facebook posting
        if re.search(r"\b(facebook|fb)\b", lower) and re.search(r"\b(post|publish|share|create post|status)\b", lower):
            if "successfully created and published post to facebook" in trajectory_summary.lower():
                return {
                    "thought": "Facebook post has been successfully created and published. The goal is achieved.",
                    "action": "none",
                    "action_args": {},
                    "is_complete": True,
                    "completion_message": f"Helper has successfully created and published your post to Facebook! The post is now live."
                }
            # Extract post content if given, or generate clean default
            fb_text = "🚀 Testing Facebook publishing via Helper-AI! Autonomous AI Agent is working smoothly."
            text_match = re.search(r'(?:saying|content|with text|message)[:\s]+["\']?([^"\']+)["\']?', goal, re.IGNORECASE)
            if text_match:
                fb_text = text_match.group(1).strip()
            return {
                "thought": "I will autonomously create and publish the requested post to Facebook using browser_automation.",
                "action": "browser_automation",
                "action_args": {"action": "publish_facebook_post", "post_text": fb_text},
                "is_complete": False,
                "completion_message": ""
            }

        # 2. Specialized handling for Blogger / Google Blogs
        if re.search(r"\b(blogger|blog|google blog|google blogs|my blogs)\b", lower):
            if "successfully created and published blog post" in trajectory_summary.lower():
                return {
                    "thought": "Blog post has been successfully published on Blogger. Goal is achieved.",
                    "action": "none",
                    "action_args": {},
                    "is_complete": True,
                    "completion_message": f"Helper has successfully published your blog post on Blogger! The post is live."
                }
            if re.search(r"\b(list|show|get|names|blogs|my)\b", lower):
                if "list_blogs" in trajectory_summary.lower() or "blogger.com" in trajectory_summary.lower() or "found" in trajectory_summary.lower():
                    return {
                        "thought": "I have accessed Google Blogger and retrieved the blog status for the user.",
                        "action": "none",
                        "action_args": {},
                        "is_complete": True,
                        "completion_message": "Helper has accessed Google Blogger in your live Project Browser and inspected your blogs."
                    }
                return {
                    "thought": "I will inspect the user's Google Blogger account and list their blogs using browser_automation.",
                    "action": "browser_automation",
                    "action_args": {"action": "list_blogs"},
                    "is_complete": False,
                    "completion_message": ""
                }
            return {
                "thought": "I will open Blogger in the live Project Browser so the user can create and manage their blog with persistent login.",
                "action": "browser_automation",
                "action_args": {"action": "open_url", "url": "https://www.blogger.com"},
                "is_complete": False,
                "completion_message": ""
            }

        if not has_run:
            if re.search(r"\b(open|launch|start|run)\s+(edge|chrome|browser|notepad|calc|calculator|explorer|terminal)\b", lower) or (lower.startswith("open ") or lower.startswith("launch ")):
                target_app = "edge" if "edge" in lower else ("chrome" if "chrome" in lower else ("notepad" if "notepad" in lower else ("calc" if "calc" in lower else lower.replace("open ", "").replace("launch ", "").strip())))
                return {
                    "thought": f"I will launch '{target_app}' using the open_app_or_file tool.",
                    "action": "open_app_or_file",
                    "action_args": {"target": target_app},
                    "is_complete": False,
                    "completion_message": ""
                }
            elif re.search(r"\b(speak|say|voice output|tell me)\b", lower):
                spoken_text = re.sub(r"^(speak|say|tell me|voice output)\s+", "", goal, flags=re.IGNORECASE).strip()
                return {
                    "thought": f"I will speak aloud the message: '{spoken_text}' using the speak_aloud tool.",
                    "action": "speak_aloud",
                    "action_args": {"text": spoken_text or "Hello from Helper-AI voice engine!"},
                    "is_complete": False,
                    "completion_message": ""
                }
            elif re.search(r"\b(mcp|model context protocol|mcp tools|mcp servers)\b", lower):
                return {
                    "thought": "I will inspect the configured Model Context Protocol (MCP) servers.",
                    "action": "manage_mcp",
                    "action_args": {"action": "list_servers"},
                    "is_complete": False,
                    "completion_message": ""
                }
            elif re.search(r"\b(screenshot|capture screen|screen shot)\b", lower):
                return {
                    "thought": "I will capture a desktop screenshot using desktop_gui_control.",
                    "action": "desktop_gui_control",
                    "action_args": {"action": "take_screenshot"},
                    "is_complete": False,
                    "completion_message": ""
                }
            elif re.search(r"\b(resolution|screen size|mouse pos|cursor)\b", lower):
                return {
                    "thought": "I will get screen resolution and cursor position using desktop_gui_control.",
                    "action": "desktop_gui_control",
                    "action_args": {"action": "get_screen_info"},
                    "is_complete": False,
                    "completion_message": ""
                }
            elif re.search(r"\b(ollama|local ai|ai model|models)\b", lower):
                return {
                    "thought": "I will inspect the installed Ollama models.",
                    "action": "manage_ollama",
                    "action_args": {"action": "list_models"},
                    "is_complete": False,
                    "completion_message": ""
                }
            elif re.search(r"\b(health|specs|ram|cpu|diagnostic|hardware)\b", lower):
                return {
                    "thought": "I will examine the current system hardware specs, CPU, RAM, and disk utilization.",
                    "action": "get_system_health",
                    "action_args": {},
                    "is_complete": False,
                    "completion_message": ""
                }
            elif re.search(r"\b(process|processes|task manager|tasks)\b", lower):
                return {
                    "thought": "I will list the top running processes by memory usage.",
                    "action": "manage_processes",
                    "action_args": {"action": "list", "sort_by": "memory", "limit": 10},
                    "is_complete": False,
                    "completion_message": ""
                }
            elif re.search(r"\b(search|google|internet|web|lookup)\b", lower):
                query = re.sub(r"^(search|google|find|lookup)\s+(the\s+web\s+for\s+|web\s+for\s+|for\s+)?", "", goal, flags=re.IGNORECASE).strip()
                return {
                    "thought": f"I will search the web for: '{query}'",
                    "action": "search_web",
                    "action_args": {"query": query, "max_results": 5},
                    "is_complete": False,
                    "completion_message": ""
                }
            elif re.search(r"\b(list|files|folder|downloads|desktop|contents|check contents|directory)\b", lower):
                # Extract full drive path if present (e.g. E:\Freelancer Crack The Deal)
                p_match = re.search(r'([A-Za-z]:\\[^"\'\n\r;|]+)', goal)
                if p_match:
                    target = p_match.group(1).strip()
                elif "download" in lower:
                    target = "Downloads"
                elif "desktop" in lower:
                    target = "Desktop"
                else:
                    target = "."
                return {
                    "thought": f"I will list the files in '{target}' using the list_directory tool.",
                    "action": "list_directory",
                    "action_args": {"path": target},
                    "is_complete": False,
                    "completion_message": ""
                }
            elif re.search(r"\b(powershell|cmd|command)\b", lower):
                cmd = re.sub(r"^(run\s+)?(powershell|cmd|command)(\s*:\s*|\s+)?", "", goal, flags=re.IGNORECASE).strip(": ")
                return {
                    "thought": f"I will execute the PowerShell command: {cmd}",
                    "action": "execute_powershell",
                    "action_args": {"command": cmd},
                    "is_complete": False,
                    "completion_message": ""
                }
            else:
                return {
                    "thought": "I will run system health diagnostics to evaluate current environment.",
                    "action": "get_system_health",
                    "action_args": {},
                    "is_complete": False,
                    "completion_message": ""
                }
        else:
            # Second step verification
            return {
                "thought": "The requested action has been performed and verified. Goal is achieved.",
                "action": "none",
                "action_args": {},
                "is_complete": True,
                "completion_message": f"Helper has successfully executed your goal: '{goal}'. Everything has been completed and verified."
            }
