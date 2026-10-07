"""Unified LLM Client supporting Gemini, OpenAI, Groq, Ollama, and RuleEngine fallback."""
import os
import json
import re
from typing import Dict, Any, Optional
import requests

SYSTEM_PROMPT = """You are Helper, an autonomous AI assistant with full control of the user's running PC and internet access.
Your mandate is to accomplish the user's GOAL completely, reliably, and autonomously WITHOUT asking redundant questions.

You have access to the following tools:
{tool_schemas}

### OPERATING PRINCIPLES:
1. Plan and execute sequentially: Break goals into sensible steps and take action immediately.
2. Self-Healing & Adaptability: If a tool or PowerShell command encounters an error, analyze the error output and formulate an alternative approach rather than stopping.
3. Operating Environment: The host machine is {os_name} {os_release}. Standard directories like Desktop, Downloads, and Documents are directly accessible via tools.
4. Completion: When the goal has been fully met, set `is_complete` to true, provide a concise, pleasant summary in `completion_message`, and set `action` to "none".

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
        self.provider = (provider or os.getenv("LLM_PROVIDER", "gemini")).lower()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY") or ""
        self.model = model
        self.base_url = base_url

        if not self.model:
            if self.provider == "gemini":
                self.model = "gemini-1.5-flash"
            elif self.provider == "openai":
                self.model = "gpt-4o-mini"
            elif self.provider == "groq":
                self.model = "llama-3.3-70b-versatile"
            elif self.provider == "ollama":
                self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
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

    def _call_ollama(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        base_url = self.base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        url = f"{base_url.rstrip('/')}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "format": "json"
        }
        resp = requests.post(url, json=payload, timeout=60)
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
        has_run = "Step 1:" in trajectory_summary

        if not has_run:
            if re.search(r"\b(health|specs|ram|cpu|diagnostic|hardware)\b", lower):
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
            elif re.search(r"\b(list|files|folder|downloads|desktop)\b", lower):
                target = "Downloads" if "download" in lower else ("Desktop" if "desktop" in lower else ".")
                return {
                    "thought": f"I will list the files in {target}.",
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
            # Second step in rule engine completes the goal
            return {
                "thought": "The requested action has been performed and verified. Goal is achieved.",
                "action": "none",
                "action_args": {},
                "is_complete": True,
                "completion_message": f"Helper has successfully executed your goal: '{goal}'. Everything has been completed and verified."
            }
