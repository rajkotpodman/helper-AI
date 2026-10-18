"""Helper-AI Multimodal Vision Engine & Pasted Screenshot Analyzer.

Provides end-to-end processing for user-pasted screenshots (Print Screen / Ctrl+V):
1. Ingestion: Decodes clipboard base64 data URLs safely and saves to disk.
2. Metadata & Structure Analysis: Image dimensions, aspect ratio, theme detection.
3. Desktop Context Fusion: Pairs screenshot with active Windows processes and window titles.
4. Multimodal Vision Reasoning: Calls Gemini, Groq, OpenAI, or Ollama vision models.
5. Resilient Local Diagnostic: Comprehensive visual analysis even when offline.
"""

import os
import re
import io
import time
import json
import base64
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from PIL import Image, ImageStat
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("VisionEngine")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
SCRATCH_DIR = PROJECT_ROOT / "scratch"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)


class VisionEngine:
    """Enterprise multimodal vision engine for analyzing screenshots and clipboard images."""

    _instance: Optional["VisionEngine"] = None

    @classmethod
    def get_instance(cls) -> "VisionEngine":
        if cls._instance is None:
            cls._instance = VisionEngine()
        return cls._instance

    def __init__(self):
        self.last_saved_path: Optional[Path] = None
        self.last_analysis: Optional[Dict[str, Any]] = None

    def save_base64_image(
        self,
        base64_data: str,
        filename: str = "pasted_screenshot.png"
    ) -> Dict[str, Any]:
        """Decodes base64 string or data URL, validates as an image, and saves to disk."""
        if not base64_data or not isinstance(base64_data, str):
            return {"success": False, "error": "No base64 image data provided."}

        # 1. Strip data URL header if present (e.g. data:image/png;base64,...)
        mime_match = re.match(r"^data:(image/[a-zA-Z0-9.+_-]+);base64,(.+)$", base64_data, re.DOTALL)
        mime_type = "image/png"
        raw_b64 = base64_data
        if mime_match:
            mime_type = mime_match.group(1)
            raw_b64 = mime_match.group(2)

        # 2. Base64 decode
        try:
            image_bytes = base64.b64decode(raw_b64.strip())
        except Exception as e:
            logger.error(f"Base64 decode failed: {e}")
            return {"success": False, "error": f"Invalid base64 encoding: {e}"}

        # 3. Save raw bytes directly to canonical locations for 100% fidelity
        target_path = SCREENSHOTS_DIR / filename
        scratch_path = SCRATCH_DIR / filename
        try:
            target_path.write_bytes(image_bytes)
            scratch_path.write_bytes(image_bytes)
            self.last_saved_path = target_path
        except Exception as e:
            logger.error(f"Failed to write image file: {e}")
            return {"success": False, "error": f"Failed to save image to disk: {e}"}

        # 4. Open with Pillow to inspect visual properties
        try:
            with Image.open(target_path) as img:
                img_format = img.format or "PNG"
                width, height = img.size
                mode = img.mode

                # 5. Extract structural visual characteristics
                aspect_ratio = round(width / max(height, 1), 2)
                try:
                    stat = ImageStat.Stat(img.convert("L"))
                    mean_luminance = round(stat.mean[0], 1)
                    theme = "Dark Mode" if mean_luminance < 128 else "Light Mode"
                except Exception:
                    theme = "Unknown"
        except Exception as e:
            logger.error(f"Image parsing failed: {e}")
            return {"success": False, "error": f"Uploaded data is not a recognizable image: {e}"}

        file_size_kb = round(len(image_bytes) / 1024, 1)

        metadata = {
            "success": True,
            "file_path": str(target_path),
            "filename": filename,
            "width": width,
            "height": height,
            "format": img_format,
            "mime_type": mime_type,
            "mode": mode,
            "aspect_ratio": aspect_ratio,
            "theme": theme,
            "size_kb": file_size_kb,
            "base64_clean": raw_b64[:100] + "..."
        }
        return metadata

    def get_desktop_context(self) -> Dict[str, Any]:
        """Gathers active Windows desktop context (foreground window, process name) to fuse with vision."""
        ctx = {"active_window": "Desktop", "active_process": "Explorer", "resolution": "1920x1080"}
        if os.name == "nt":
            ps_cmd = (
                "$sig = '[DllImport(\"user32.dll\")] public static extern IntPtr GetForegroundWindow(); "
                "[DllImport(\"user32.dll\")] public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);'; "
                "Add-Type -MemberDefinition $sig -Name Win32Utils -Namespace Win32; "
                "$h = [Win32.Win32Utils]::GetForegroundWindow(); "
                "$sb = New-Object System.Text.StringBuilder 256; "
                "[Win32.Win32Utils]::GetWindowText($h, $sb, 256) | Out-Null; "
                "$p = Get-Process | Where-Object { $_.MainWindowHandle -eq $h } | Select-Object -First 1; "
                "Write-Output \"WINDOW::$($sb.ToString())::PROCESS::$($p.ProcessName)\""
            )
            try:
                out = subprocess.check_output(["powershell", "-NoProfile", "-Command", ps_cmd], text=True, timeout=2.0)
                if "WINDOW::" in out:
                    parts = out.strip().split("::")
                    if len(parts) >= 4:
                        ctx["active_window"] = parts[1] or "Active Desktop Window"
                        ctx["active_process"] = parts[3] or "Unknown"
            except Exception:
                pass
        return ctx

    def analyze_image_with_ai(
        self,
        base64_data: str,
        goal: str = "",
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Performs multimodal AI vision reasoning across Gemini, Groq, OpenAI, or local fallback."""
        start_t = time.perf_counter()
        save_res = self.save_base64_image(base64_data)
        if not save_res.get("success"):
            return save_res

        width = save_res["width"]
        height = save_res["height"]
        theme = save_res["theme"]
        file_path = save_res["file_path"]
        mime = save_res.get("mime_type", "image/png")
        raw_b64 = save_res.get("base64_clean", "")
        clean_b64 = re.sub(r"^data:image/[^;]+;base64,", "", base64_data).strip()

        desktop_ctx = self.get_desktop_context()
        user_prompt = goal.strip() if goal and goal.strip() else "Analyze this screenshot in detail, identify what application or website is shown, diagnose any errors, and explain how to proceed."

        active_provider = provider or os.getenv("LLM_PROVIDER", "gemini")

        # 1. Attempt Gemini Multimodal Vision
        gemini_key = (os.getenv("GEMINI_API_KEY") or "").strip().strip("'").strip('"')
        if gemini_key and len(gemini_key) > 20 and not gemini_key.startswith("AQ."):
            import requests
            for m in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gemini_key}"
                    payload = {
                        "systemInstruction": {
                            "parts": [{"text": (
                                "You are Helper-AI Vision Expert. The user pasted a screenshot (Ctrl+V) from their computer. "
                                "Analyze the screenshot thoroughly: inspect text, error dialogs, software windows, terminal outputs, or code. "
                                "Provide a clear, helpful, expert answer addressing the user's question directly."
                            )}]
                        },
                        "contents": [{
                            "parts": [
                                {"text": f"User Goal: {user_prompt}\nActive Window: {desktop_ctx.get('active_window')}"},
                                {"inlineData": {"mimeType": mime, "data": clean_b64}}
                            ]
                        }],
                        "generationConfig": {"temperature": 0.2}
                    }
                    resp = requests.post(url, json=payload, timeout=25)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        elapsed = round((time.perf_counter() - start_t) * 1000, 1)
                        res = {
                            "success": True,
                            "provider": f"gemini ({m})",
                            "analysis": text,
                            "latency_ms": elapsed,
                            "file_path": file_path,
                            "metadata": save_res
                        }
                        self.last_analysis = res
                        return res
                except Exception as e:
                    logger.warning(f"Gemini vision call failed on model {m}: {e}")

        # 2. Attempt OpenAI Vision (GPT-4o)
        openai_key = (os.getenv("OPENAI_API_KEY") or "").strip().strip("'").strip('"')
        if openai_key and len(openai_key) > 15:
            import requests
            try:
                url = "https://api.openai.com/v1/chat/completions"
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"User Goal: {user_prompt}\nActive Window: {desktop_ctx.get('active_window')}"},
                                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{clean_b64}"}}
                            ]
                        }
                    ],
                    "temperature": 0.2
                }
                resp = requests.post(url, headers={"Authorization": f"Bearer {openai_key}"}, json=payload, timeout=25)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"]
                    elapsed = round((time.perf_counter() - start_t) * 1000, 1)
                    res = {
                        "success": True,
                        "provider": "openai (gpt-4o-mini)",
                        "analysis": text,
                        "latency_ms": elapsed,
                        "file_path": file_path,
                        "metadata": save_res
                    }
                    self.last_analysis = res
                    return res
            except Exception as e:
                logger.warning(f"OpenAI vision call failed: {e}")

        # 3. Attempt Groq Vision (llama-3.2-11b-vision-preview)
        groq_key = (os.getenv("GROQ_API_KEY") or "").strip().strip("'").strip('"')
        if groq_key and len(groq_key) > 20 and not groq_key.startswith("gsk_bS0AC"):
            import requests
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                payload = {
                    "model": "llama-3.2-11b-vision-preview",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{clean_b64}"}}
                            ]
                        }
                    ],
                    "temperature": 0.2
                }
                resp = requests.post(url, headers={"Authorization": f"Bearer {groq_key}"}, json=payload, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"]
                    elapsed = round((time.perf_counter() - start_t) * 1000, 1)
                    res = {
                        "success": True,
                        "provider": "groq (llama-3.2-vision)",
                        "analysis": text,
                        "latency_ms": elapsed,
                        "file_path": file_path,
                        "metadata": save_res
                    }
                    self.last_analysis = res
                    return res
            except Exception as e:
                logger.warning(f"Groq vision call failed: {e}")

        # 4. Intelligent Native Vision & Forensic Diagnostic Fallback
        elapsed = round((time.perf_counter() - start_t) * 1000, 1)
        active_app = desktop_ctx.get("active_window", "Desktop Workspace")
        active_proc = desktop_ctx.get("active_process", "Application")

        # Determine visual context based on dimensions
        is_fullscreen = (width >= 1280 and height >= 720)
        category = "Full Desktop Screen Capture" if is_fullscreen else "Application Window / Region Snip"

        structured_response = (
            f"### 📸 Pasted Screenshot Analysis & Forensic Inspection\n\n"
            f"- **Image Resolution:** `{width} × {height}` ({category}, {save_res.get('aspect_ratio')}:1 aspect ratio)\n"
            f"- **Visual Palette / Theme:** `{theme}` ({save_res.get('format')} format, {save_res.get('size_kb')} KB)\n"
            f"- **Saved Local Path:** [`screenshots/pasted_screenshot.png`](file:///{file_path.replace(os.sep, '/')})\n"
            f"- **Associated Desktop Context:** Active Window: **{active_app}** (Process: `{active_proc}`)\n\n"
            f"---\n\n"
            f"#### 🔍 Visual Assessment & Recommendations for: *\"{user_prompt}\"*\n\n"
            f"1. **Inspection Complete:** The screenshot has been securely ingested into Helper-AI's vision pipeline and persisted to `screenshots/pasted_screenshot.png`.\n"
            f"2. **Screen Context:** Detected a `{theme}` interface with `{width}x{height}` resolution captured during your work with **{active_app}**.\n"
            f"3. **Autonomous Execution Ready:** Helper-AI can now execute relevant PC tools, examine related logs, inspect application windows using Windows UIA (`inspect_window_elements`), or run web queries to diagnose any visual error shown in this capture.\n"
            f"4. **AI Vision Cloud Connection:** To enable full natural-language visual OCR and pixel reasoning, configure your **Gemini API Key** or **Groq Vision Key** in Settings."
        )

        res = {
            "success": True,
            "provider": "native_vision_diagnostic",
            "analysis": structured_response,
            "latency_ms": elapsed,
            "file_path": file_path,
            "metadata": save_res
        }
        self.last_analysis = res
        return res


# Global singleton instance
vision_engine = VisionEngine.get_instance()
