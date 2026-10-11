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
7. Repetition & Multiple Tasks / Loops: When the user requests a task to be performed multiple times or for multiple items (e.g. "loop 5 times", "apply in 5 spaces/jobs", "repeat 3 times", "do this 5 times"):
- You MUST ensure the task runs for the FULL requested count (e.g. all 5 items).
- NEVER declare completion (`is_complete: true`) or stop after just 1 item if the user requested 5.
- If an individual item or step encounters an error or popup, DO NOT stop or quit! Handle or discard the failed item, skip to the next item, and keep looping until the target count is satisfied.
- In tool parameters, pass the full requested count (e.g. "count": 5).
8. Form Filling & Browser Popups: When automating browser forms, always handle modal popups, dropdown `<select>` options, comboboxes, and post-submission dialogs ("Done", "Close", "Not now", "Dismiss") cleanly so you can proceed to the next step.
9. Folder Paths with Spaces: When checking the contents of ANY folder (e.g. `E:\Freelancer Crack The Deal`), ALWAYS use the `list_directory` tool with `path: "E:\\Freelancer Crack The Deal"`. Do NOT run raw PowerShell commands like `Get-ChildItem` for listing files. If you do use PowerShell, paths with spaces MUST be wrapped in double quotes: `Get-ChildItem "E:\Freelancer Crack The Deal"`.
10. Opening Applications: When the user's goal is to open or launch an application (e.g. 'open edge', 'launch notepad', 'open browser'), use the `open_app_or_file` tool with target='edge' (or target='notepad', target='chrome', etc.). Once launched successfully, the goal IS COMPLETE! Immediately set `is_complete: true`, `action: 'none'`, and inform the user. DO NOT close or terminate the app, and DO NOT loop checking processes!
11. Live Project Browser Control: To automate websites, create blogs, post to LinkedIn/Facebook, click buttons, or fill forms, use `browser_automation`:
- Apply to LinkedIn Jobs with CV (1-step autonomous): Action: "browser_automation", Action args: {{ "action": "apply_linkedin_jobs", "keywords": "Technical Support", "resume_path": "C:\\Users\\DELL\\Downloads\\Jignesh_Kariya_CV (1).docx", "count": 5 }}
- Create & Publish LinkedIn Post (1-step autonomous): Action: "browser_automation", Action args: {{ "action": "publish_linkedin_post", "post_text": "My LinkedIn post text..." }}
- Create & Publish Facebook Post (1-step autonomous): Action: "browser_automation", Action args: {{ "action": "publish_facebook_post", "post_text": "My Facebook post text..." }}
- Create & Publish Blogger Post (1-step autonomous): Action: "browser_automation", Action args: {{ "action": "publish_blog_post", "title": "My Blog Title", "text": "My post body..." }}
- Read / Fetch Full Webpage Content: Action: "browser_automation", Action args: {{ "action": "fetch_full_page", "url": "https://..." }} (or use tool "fetch_web_content", args: {{ "url": "https://..." }})
- Scroll Webpage: Action: "browser_automation", Action args: {{ "action": "scroll", "direction": "down", "pixels": 800 }}
- Open URL: Action: "browser_automation", Action args: {{ "action": "open_url", "url": "https://www.linkedin.com/feed" }}
- Click button/link by text: Action: "browser_automation", Action args: {{ "action": "click", "target": "Start a post" }} (or "Post", "Sign in", "New Post")
- Type into text boxes: Action: "browser_automation", Action args: {{ "action": "type", "target": "Share your thoughts", "text": "My post content" }}
- Select dropdown option: Action: "browser_automation", Action args: {{ "action": "select_dropdown", "target": "country", "option": "India" }}
- Dismiss popups/modals: Action: "browser_automation", Action args: {{ "action": "dismiss_popups" }}
- List open browser tabs: Action: "browser_automation", Action args: {{ "action": "list_tabs" }}
- Switch to a browser tab: Action: "browser_automation", Action args: {{ "action": "switch_tab", "target": "Google" }} (or index "0", "1")
- Close a browser tab: Action: "browser_automation", Action args: {{ "action": "close_tab" }}
- Sign up / Sign in with Google (Yahoo, etc.):
  Start at the main login page (e.g. "https://login.yahoo.com/"), click "Sign in with Google" (DO NOT use /registration URLs which block automated traffic with 403 Forbidden). When Google Accounts chooser opens, select the logged-in Google account or click "Continue as".
This controls the live project browser where logins and cookies are permanently remembered.

### QUICK TOOL ROUTING CHEATSHEET:
- Fetching / Reading full web page content:
  Action: "fetch_web_content", Action args: {{ "url": "https://..." }} OR Action: "browser_automation", Action args: {{ "action": "fetch_full_page", "url": "https://..." }}
- Searching the web or internet:
  Action: "search_web", Action args: {{ "query": "..." }}
- Downloading internet files:
  Action: "download_file", Action args: {{ "url": "https://...", "destination_path": "Downloads/file.pdf" }}
- LinkedIn job applications with CV / Easy Apply:
  Action: "browser_automation", Action args: {{ "action": "apply_linkedin_jobs", "keywords": "...", "resume_path": "C:\\Users\\DELL\\Downloads\\Jignesh_Kariya_CV (1).docx", "count": 5 }}
- LinkedIn post creation & publishing:
  Action: "browser_automation", Action args: {{ "action": "publish_linkedin_post", "post_text": "..." }}
- Facebook post creation & publishing:
  Action: "browser_automation", Action args: {{ "action": "publish_facebook_post", "post_text": "..." }}
- Blogger post creation & publishing:
  Action: "browser_automation", Action args: {{ "action": "publish_blog_post", "title": "...", "text": "..." }}
- Live Web browsing / clicking buttons / web forms:
  Action: "browser_automation", Action args: {{ "action": "open_url", "url": "https://..." }}
- Desktop PC Human Automation (Keyboard shortcuts, Mouse clicks, Windows):
  - Hotkey / Shortcut (Ctrl+C, Ctrl+V, Alt+Tab, Win+R, Ctrl+S): Action: "desktop_gui_control", Action args: {{ "action": "hotkey", "keys": "ctrl+c" }}
  - Click anywhere on screen: Action: "desktop_gui_control", Action args: {{ "action": "click_screen", "x": 500, "y": 300 }}
  - Right click or Double click: Action: "desktop_gui_control", Action args: {{ "action": "right_click" }} / {{ "action": "double_click" }}
  - Scroll mouse wheel: Action: "desktop_gui_control", Action args: {{ "action": "scroll", "clicks": -500 }}
  - Copy/Read Windows Clipboard: Action: "desktop_gui_control", Action args: {{ "action": "clipboard_copy", "text": "..." }} / {{ "action": "clipboard_paste" }}
  - List open desktop applications/windows: Action: "desktop_gui_control", Action args: {{ "action": "list_windows" }}
  - Focus / Switch to a window: Action: "desktop_gui_control", Action args: {{ "action": "focus_window", "target": "Notepad" }}
  - Take desktop screenshot: Action: "desktop_gui_control", Action args: {{ "action": "take_screenshot" }}
- Opening / Launching applications:
  Action: "open_app_or_file", Action args: {{ "target": "edge" }} (or "notepad", "chrome", "calc")
- Checking Ollama models / local models / AI status:
  Action: "manage_ollama", Action args: {{ "action": "list_models" }}
- Inspecting or listing files in a folder (especially with spaces):
  Action: "list_directory", Action args: {{ "path": "E:\\Freelancer Crack The Deal" }}
- Checking PC health, RAM, CPU, or hardware:
  Action: "get_system_health", Action args: {{}}
- Running PowerShell / CMD scripts:
  Action: "execute_powershell", Action args: {{ "command": "..." }}
- Managing processes:
  Action: "manage_processes", Action args: {{ "action": "list", "sort_by": "memory", "limit": 10 }}
- Voice speech synthesis / speak aloud:
  Action: "speak_aloud", Action args: {{ "text": "..." }}
- Playwright vision browser / visual screenshot:
  Action: "vision_browser", Action args: {{ "action": "screenshot" }}
- Model Context Protocol (MCP) servers & tools:
  Action: "manage_mcp", Action args: {{ "action": "list_servers" }}

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
                self.model = os.getenv("GEMINI_MODEL") or "gemini-flash-latest"
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
            # If current provider failed (e.g. Groq 429 rate limit), check if Gemini key is available for seamless failover!
            gemini_key = os.getenv("GEMINI_API_KEY")
            if self.provider != "gemini" and gemini_key:
                try:
                    self.provider = "gemini"
                    self.api_key = gemini_key.strip().strip("'").strip('"')
                    self.model = os.getenv("GEMINI_MODEL") or "gemini-flash-latest"
                    step = self._call_gemini(sys_prompt, user_content)
                    step["thought"] = f"(Note: Switched to Gemini after provider error: {str(e)[:80]}...) " + step.get("thought", "")
                    return step
                except Exception as ge:
                    pass

            # Fallback to rule engine if API calls fail
            step = self._rule_engine_step(goal, trajectory_summary)
            step["thought"] = f"(Note: LLM provider {self.provider} error: {str(e)}. Using autonomous fallback.) " + step["thought"]
            return step

    def _call_gemini(self, system_instruction: str, user_prompt: str) -> Dict[str, Any]:
        target_model = self.model or "gemini-flash-latest"
        gemini_candidates = [
            target_model,
            "gemini-flash-latest",
            "gemini-flash-lite-latest",
            "gemini-3.5-flash",
            "gemini-3-flash-preview",
            "gemini-2.5-flash"
        ]
        # Deduplicate
        seen = set()
        candidates = []
        for c in gemini_candidates:
            if c not in seen:
                seen.add(c)
                candidates.append(c)

        last_error = None
        for m in candidates:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
                payload = {
                    "systemInstruction": {"parts": [{"text": system_instruction}]},
                    "contents": [{"parts": [{"text": user_prompt}]}],
                    "generationConfig": {
                        "temperature": 0.2,
                        "responseMimeType": "application/json"
                    }
                }
                resp = requests.post(url, json=payload, timeout=45)
                if resp.status_code == 200:
                    self.model = m
                    data = resp.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return self._parse_json_response(raw_text)
                else:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:150]}"
            except Exception as e:
                last_error = str(e)
                continue

        raise RuntimeError(f"Gemini API call failed across models {candidates}. Last error: {last_error}")

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
            # 1. Check if Groq returned failed_generation inside a tool_use_failed 400 error
            failed_gen = None
            if hasattr(e, "body") and isinstance(e.body, dict):
                failed_gen = e.body.get("error", {}).get("failed_generation")
            elif hasattr(e, "response"):
                try:
                    err_json = e.response.json()
                    failed_gen = err_json.get("error", {}).get("failed_generation")
                except Exception:
                    pass
            if not failed_gen:
                m = re.search(r"['\"]failed_generation['\"]:\s*['\"](\{.*?\})['\"]", str(e))
                if m:
                    failed_gen = m.group(1)

            if failed_gen:
                try:
                    parsed = self._parse_json_response(failed_gen)
                    if parsed.get("action") and parsed.get("action") != "none":
                        return parsed
                except Exception:
                    pass

            err_str = str(e).lower()
            # If rate limit (429 / TPD / TPM), model not found, or tool_use_failed (400), try alternative models
            if any(k in err_str for k in ["429", "rate_limit", "rate limit", "tpd", "tokens per day", "model_not_found", "404", "does not exist", "tool_use_failed", "tool choice is none", "400"]):
                alt_candidates = [
                    "openai/gpt-oss-120b",
                    "openai/gpt-oss-20b",
                    "qwen/qwen3.8-27b",
                    "allam-2-7b"
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
                    except Exception as alt_err:
                        alt_failed = None
                        if hasattr(alt_err, "body") and isinstance(alt_err.body, dict):
                            alt_failed = alt_err.body.get("error", {}).get("failed_generation")
                        if alt_failed:
                            try:
                                return self._parse_json_response(alt_failed)
                            except Exception:
                                pass
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

        parsed = None
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            # Attempt to extract JSON substring
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except Exception:
                    pass

        if isinstance(parsed, dict):
            # Normalize action name across Helper-AI, OpenAI, Groq, and function-call schemas
            action = parsed.get("action") or parsed.get("name") or parsed.get("tool") or "none"
            # Normalize action args
            action_args = parsed.get("action_args") or parsed.get("arguments") or parsed.get("parameters") or parsed.get("args") or {}
            if isinstance(action_args, str):
                try:
                    action_args = json.loads(action_args)
                except Exception:
                    action_args = {}
            if not isinstance(action_args, dict):
                action_args = {}

            # Normalize thought
            thought = parsed.get("thought") or parsed.get("reasoning") or parsed.get("description") or f"Executing tool '{action}'."
            is_complete = bool(parsed.get("is_complete", False))
            if str(action).lower() in ["none", "complete", "finish", "done"] and not is_complete:
                is_complete = True

            return {
                "thought": thought,
                "action": action,
                "action_args": action_args,
                "is_complete": is_complete,
                "completion_message": parsed.get("completion_message") or parsed.get("message") or ""
            }

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

        # 1. Specialized handling for LinkedIn Job Applications with CV
        if re.search(r"\b(linkedin|linked in|linkdin)\b", lower) and re.search(r"\b(apply|job|jobs|opening|openings|cv|resume)\b", lower):
            # Extract count (e.g. 5 space, 5 jobs, loop 5 times)
            count = 5
            count_match = re.search(r'\b(\d+)\s*(?:space|job|jobs|position|positions|opening|openings|times)?\b', lower)
            if count_match:
                try:
                    count = int(count_match.group(1))
                except Exception:
                    count = 5

            more_match = re.search(r'more\s*(?:than\s*)?(\d+)', lower)
            if more_match:
                try:
                    count = max(count, int(more_match.group(1)))
                except Exception:
                    pass

            # Check if count reached in previous trajectory
            app_match = re.search(r'successfully applied to (\d+) job', trajectory_summary.lower())
            if app_match:
                applied_so_far = int(app_match.group(1))
                if applied_so_far >= count:
                    return {
                        "thought": f"All {applied_so_far} requested LinkedIn job applications have been submitted successfully. The goal is achieved.",
                        "action": "none",
                        "action_args": {},
                        "is_complete": True,
                        "completion_message": f"Helper has successfully applied to all {applied_so_far} requested jobs on LinkedIn using your CV!"
                    }
                else:
                    # Still need more jobs
                    count = max(1, count - applied_so_far)

            # Extract CV path if present
            cv_path = r"C:\Users\DELL\Downloads\Jignesh_Kariya_CV (1).docx"
            path_match = re.search(r'([A-Za-z]:\\[^"\'\n\r;|]+(?:\.docx|\.pdf|\.doc)?)', goal)
            if path_match and os.path.exists(path_match.group(1).strip()):
                cv_path = path_match.group(1).strip()

            return {
                "thought": f"I will autonomously search and apply to {count} jobs on LinkedIn using Easy Apply and attach the user's CV ({cv_path}).",
                "action": "browser_automation",
                "action_args": {
                    "action": "apply_linkedin_jobs",
                    "keywords": "Technical Support",
                    "resume_path": cv_path,
                    "count": count
                },
                "is_complete": False,
                "completion_message": ""
            }

        # 2. Specialized handling for LinkedIn posting
        if re.search(r"\b(linkedin|linked in)\b", lower) and re.search(r"\b(post|publish|share|create post|status)\b", lower):
            if "successfully created and published post to linkedin" in trajectory_summary.lower():
                return {
                    "thought": "LinkedIn post has been successfully created and published. The goal is achieved.",
                    "action": "none",
                    "action_args": {},
                    "is_complete": True,
                    "completion_message": "Helper has successfully created and published your post to LinkedIn! The post is now live on your feed."
                }
            # Extract content if given, check for file references (like HOW_TO_USE.md), or craft freelancer pitch
            li_text = ""
            # Check for file path in goal
            path_match = re.search(r'([A-Za-z]:\\[^"\'\n\r;|]+(?:\.md|\.txt)?)', goal)
            if path_match and os.path.exists(path_match.group(1).strip()):
                li_text = path_match.group(1).strip()
            if not li_text:
                text_match = re.search(r'(?:saying|content|with text|message)[:\s]+["\']?([^"\']+)["\']?', goal, re.IGNORECASE)
                if text_match:
                    li_text = text_match.group(1).strip()
                else:
                    li_text = goal

            return {
                "thought": "I will autonomously create and publish the requested post to LinkedIn using browser_automation with verification.",
                "action": "browser_automation",
                "action_args": {"action": "publish_linkedin_post", "post_text": li_text},
                "is_complete": False,
                "completion_message": ""
            }

        # 2. Specialized handling for Facebook posting
        if re.search(r"\b(facebook|fb)\b", lower) and re.search(r"\b(post|publish|share|create post|status)\b", lower):
            last_traj = trajectory_summary.lower()
            if any(k in last_traj for k in ["successfully created and published", "live on your timeline", "post published successfully"]):
                return {
                    "thought": "Facebook post has been successfully created and published. The goal is achieved.",
                    "action": "none",
                    "action_args": {},
                    "is_complete": True,
                    "completion_message": f"Helper has successfully created and published your post to Facebook! The post is now live on your timeline."
                }

            # Check if post text was already typed into composer and Post button is awaiting click
            if any(k in last_traj for k in ["post text was entered", "typed", "what's on your mind"]):
                return {
                    "thought": "Post text is entered in the composer. Clicking 'Post' to publish it immediately.",
                    "action": "browser_automation",
                    "action_args": {"action": "click", "target": "Post"},
                    "is_complete": False,
                    "completion_message": ""
                }

            # Extract post content if given, or generate clean default
            fb_text = "🚀 Testing Facebook publishing via Helper-AI! Autonomous AI Agent is working smoothly."
            text_match = re.search(r'(?:saying|content|with text|message)[:\s]+["\']?([^"\']+)["\']?', goal, re.IGNORECASE)
            if text_match:
                fb_text = text_match.group(1).strip()
            elif "http" in goal:
                url_m = re.search(r'(https?://[^\s\'"<>]+)', goal)
                if url_m:
                    fb_text = (
                        f"🚀 Check out Helper-AI: Autonomous PC Control & Internet Agent!\n\n"
                        f"Automate browser workflows, desktop tasks, form filling, and social media posting with full autonomy.\n\n"
                        f"⭐ Explore the open-source repo on GitHub:\n{url_m.group(1)}"
                    )

            return {
                "thought": "I will autonomously create, format, and publish the requested post to Facebook using browser_automation.",
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

        # 4. Specialized handling for Yahoo account with Google
        if "yahoo" in lower and any(k in lower for k in ["account", "sign in", "login", "create", "register"]):
            if "google" in lower:
                if "accounts.google.com" in trajectory_summary or "Google Accounts" in trajectory_summary:
                    return {
                        "thought": "Google account chooser is open. Selecting user's Google account to authorize Yahoo.",
                        "action": "browser_automation",
                        "action_args": {"action": "click", "target": "Continue as"},
                        "is_complete": False,
                        "completion_message": ""
                    }
                elif "login.yahoo.com" in trajectory_summary or "Sign in | Yahoo" in trajectory_summary:
                    return {
                        "thought": "On Yahoo login page. Clicking 'Sign in with Google' to initiate Google authentication.",
                        "action": "browser_automation",
                        "action_args": {"action": "click", "target": "Sign in with Google"},
                        "is_complete": False,
                        "completion_message": ""
                    }
                else:
                    return {
                        "thought": "I will open Yahoo's official login page to initiate sign-up with your logged-in Google account.",
                        "action": "browser_automation",
                        "action_args": {"action": "open_url", "url": "https://login.yahoo.com/"},
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
            elif re.search(r"\b(fetch|read|scrape|get)\s+(full\s+)?(web|webpage|page|site|url|article)\b", lower) or re.search(r'https?://[^\s]+', goal):
                url_match = re.search(r'(https?://[^\s\'"<>]+)', goal)
                target_url = url_match.group(1) if url_match else "https://en.wikipedia.org"
                return {
                    "thought": f"I will fetch the complete readable webpage content from '{target_url}' using fetch_web_content.",
                    "action": "fetch_web_content",
                    "action_args": {"url": target_url, "max_characters": 15000},
                    "is_complete": False,
                    "completion_message": ""
                }
            elif re.search(r"\b(clipboard|paste|copy to clipboard|read clipboard)\b", lower):
                if any(w in lower for w in ["paste", "read clipboard", "get clipboard"]):
                    return {
                        "thought": "I will read the Windows clipboard contents.",
                        "action": "desktop_gui_control",
                        "action_args": {"action": "clipboard_paste"},
                        "is_complete": False,
                        "completion_message": ""
                    }
                else:
                    return {
                        "thought": "I will execute clipboard copy.",
                        "action": "desktop_gui_control",
                        "action_args": {"action": "hotkey", "keys": "ctrl+c"},
                        "is_complete": False,
                        "completion_message": ""
                    }
            elif re.search(r"\b(list windows|open windows|running apps|active windows)\b", lower):
                return {
                    "thought": "I will list all open desktop application windows.",
                    "action": "desktop_gui_control",
                    "action_args": {"action": "list_windows"},
                    "is_complete": False,
                    "completion_message": ""
                }
            elif re.search(r"\b(hotkey|shortcut|press ctrl|press alt|press win)\b", lower):
                keys_m = re.search(r'(ctrl\+[a-z0-9]+|alt\+[a-z0-9]+|win\+[a-z0-9]+)', lower)
                keys = keys_m.group(1) if keys_m else "ctrl+c"
                return {
                    "thought": f"I will execute keyboard shortcut '{keys}'.",
                    "action": "desktop_gui_control",
                    "action_args": {"action": "hotkey", "keys": keys},
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
            # Multi-step autonomous self-learning discovery loop (NEVER prematurely surrender)
            last_traj = trajectory_summary.lower()

            # 1. Specialized handling for Open Source / Free Email Account with Google
            if any(k in lower for k in ["email", "mail"]) and any(k in lower for k in ["open source", "free", "platform", "account", "address"]) and "google" in lower:
                if "simplelogin" not in last_traj and "app.simplelogin.io" not in last_traj:
                    return {
                        "thought": "Previous email service was closed or unavailable. Trying SimpleLogin (100% open-source email alias & inbox service) which natively supports Google sign-in to create an email address.",
                        "action": "browser_automation",
                        "action_args": {"action": "open_url", "url": "https://app.simplelogin.io/auth/login"},
                        "is_complete": False,
                        "completion_message": ""
                    }
                elif "app.simplelogin.io" in last_traj and "google" not in last_traj:
                    return {
                        "thought": "On SimpleLogin authentication page. Clicking 'Sign in with Google' to create the email account.",
                        "action": "browser_automation",
                        "action_args": {"action": "click", "target": "Sign in with Google"},
                        "is_complete": False,
                        "completion_message": ""
                    }
                elif "accounts.google.com" in last_traj:
                    return {
                        "thought": "Google Accounts chooser is active. Clicking Google account to finish authorization.",
                        "action": "browser_automation",
                        "action_args": {"action": "click", "target": "Continue as"},
                        "is_complete": False,
                        "completion_message": ""
                    }
                else:
                    return {
                        "thought": "Reading page content to extract the newly created email address.",
                        "action": "browser_automation",
                        "action_args": {"action": "fetch_full_page"},
                        "is_complete": False,
                        "completion_message": ""
                    }

            # 2. Check if previous step had errors or couldn't find an element
            if any(err in last_traj for err in ["404", "could not find", "closed", "error", "failed", "forbidden", "403", "please wait"]):
                clean_query = re.sub(r"[^\w\s]", " ", goal).strip()
                return {
                    "thought": "Previous attempt encountered an obstacle. Searching the web for functional alternatives to solve the goal.",
                    "action": "search_web",
                    "action_args": {"query": f"{clean_query[:50]} alternative", "max_results": 5},
                    "is_complete": False,
                    "completion_message": ""
                }

            # 3. If browser is open, fetch full page content to see current state
            if "live project browser" in last_traj or "http" in last_traj:
                return {
                    "thought": "Inspecting current browser page content to determine the next action toward the goal.",
                    "action": "browser_automation",
                    "action_args": {"action": "fetch_full_page"},
                    "is_complete": False,
                    "completion_message": ""
                }

            # 4. If nothing else, discover solutions via web search without surrendering
            return {
                "thought": "Exploring alternative solutions on the web to fulfill the goal autonomously.",
                "action": "search_web",
                "action_args": {"query": goal[:60], "max_results": 5},
                "is_complete": False,
                "completion_message": ""
            }
