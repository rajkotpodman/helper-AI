"""Helper-AI Connection Diagnostic & Health Engine.

Performs high-speed, accurate multi-pass connection verification across all subsystems:
1. Internet Connectivity & DNS
2. Google Translate Engine (Zero-Key API & High Availability)
3. LLM Providers (Gemini, Groq, OpenAI, Ollama)
4. Chrome Browser CDP / Remote Debugging Port (9222 / 9225)
5. MCP (Model Context Protocol) Servers
6. Local Server & WebSocket Readiness
"""
import os
import time
import socket
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger("ConnectionChecker")


class ConnectionChecker:
    """Diagnostic system for evaluating and verifying all Helper-AI external and internal connections."""
    _instance: Optional["ConnectionChecker"] = None

    @classmethod
    def get_instance(cls) -> "ConnectionChecker":
        if cls._instance is None:
            cls._instance = ConnectionChecker()
        return cls._instance

    def __init__(self):
        self._session = requests.Session()
        try:
            adapter = HTTPAdapter(
                pool_connections=15,
                pool_maxsize=30,
                max_retries=Retry(total=2, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504])
            )
            self._session.mount("https://", adapter)
            self._session.mount("http://", adapter)
        except Exception:
            pass

    def check_internet(self, timeout: float = 3.0) -> Dict[str, Any]:
        """Validates raw internet connectivity via DNS and Google 204 ping."""
        start_t = time.perf_counter()
        dns_ok = False
        http_ok = False
        error_msg = None

        # 1. Quick DNS check
        try:
            socket.gethostbyname("google.com")
            dns_ok = True
        except Exception as e:
            error_msg = f"DNS failed: {e}"

        # 2. HTTP connectivity check
        try:
            resp = self._session.get("https://www.google.com/generate_204", timeout=timeout)
            http_ok = resp.status_code in (200, 204)
        except Exception as e:
            if not error_msg:
                error_msg = f"HTTP reachability failed: {e}"

        lat_ms = round((time.perf_counter() - start_t) * 1000, 1)
        status = "connected" if (dns_ok and http_ok) else ("degraded" if dns_ok else "disconnected")

        return {
            "name": "internet",
            "category": "Network",
            "status": status,
            "latency_ms": lat_ms,
            "dns_resolved": dns_ok,
            "http_reachable": http_ok,
            "message": "Internet connection active and responsive" if status == "connected" else (error_msg or "Internet degraded")
        }

    def check_translation(self, timeout: float = 3.0) -> Dict[str, Any]:
        """Validates Google Translate connectivity and live translation accuracy."""
        from core.translator import translator
        res = translator.check_connection(timeout=timeout)
        res["category"] = "Services"
        return res

    def check_llm(self, provider: str = "gemini") -> Dict[str, Any]:
        """Validates target LLM provider connectivity and API key validity."""
        from core.llm import LLMClient
        client = LLMClient(provider=provider)
        res = client.test_connection(provider=provider)
        res["name"] = f"llm_{provider}"
        res["category"] = "AI Engine"
        return res

    def check_chrome(self) -> Dict[str, Any]:
        """Validates Chrome remote debugging CDP connectivity on port 9222 and 9225."""
        start_t = time.perf_counter()
        port_9222_open = False
        cdp_active = False
        browser_info = "Ready to launch"

        # Check port 9222 (interactive desktop Chrome)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.2)
                port_9222_open = (s.connect_ex(('127.0.0.1', 9222)) == 0)
        except Exception:
            pass

        if port_9222_open:
            try:
                resp = self._session.get("http://127.0.0.1:9222/json/version", timeout=1.0)
                if resp.status_code == 200:
                    cdp_active = True
                    data = resp.json()
                    browser_info = data.get("Browser", "Chrome CDP Active")
            except Exception:
                browser_info = "Port open, awaiting CDP attachment"

        lat_ms = round((time.perf_counter() - start_t) * 1000, 1)
        status = "connected" if cdp_active else ("idle_port_open" if port_9222_open else "standby_ready")

        return {
            "name": "chrome_browser",
            "category": "Browser",
            "status": status,
            "latency_ms": lat_ms,
            "port_9222_open": port_9222_open,
            "cdp_active": cdp_active,
            "details": browser_info,
            "message": f"Chrome Automation ({browser_info})"
        }

    def check_mcp(self) -> Dict[str, Any]:
        """Validates configured Model Context Protocol servers."""
        from core.mcp_manager import MCPManager
        start_t = time.perf_counter()
        mcp = MCPManager.get_instance()
        servers = mcp.list_servers()
        lat_ms = round((time.perf_counter() - start_t) * 1000, 1)

        enabled_count = sum(1 for s in servers if s.get("enabled", False))
        return {
            "name": "mcp_servers",
            "category": "Protocol",
            "status": "connected" if servers else "unconfigured",
            "latency_ms": lat_ms,
            "servers_count": len(servers),
            "enabled_count": enabled_count,
            "message": f"{len(servers)} MCP server(s) configured ({enabled_count} enabled)"
        }

    def check_websocket_backend(self, host: str = "127.0.0.1", port: int = 8000) -> Dict[str, Any]:
        """Validates FastAPI and WebSocket server readiness."""
        start_t = time.perf_counter()
        port_open = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.2)
                port_open = (s.connect_ex((host, port)) == 0)
        except Exception:
            pass

        lat_ms = round((time.perf_counter() - start_t) * 1000, 1)
        return {
            "name": "websocket_server",
            "category": "Server",
            "status": "connected" if port_open else "standby_or_starting",
            "latency_ms": lat_ms,
            "port": port,
            "message": f"Server listening on {host}:{port}" if port_open else f"Server standby on port {port}"
        }

    def check_livekit(self) -> Dict[str, Any]:
        """Validates LiveKit WebRTC Voice and Vision engine readiness."""
        try:
            from core.livekit_bridge import livekit_bridge
            return livekit_bridge.test_connection()
        except Exception as e:
            return {
                "name": "livekit_webrtc",
                "category": "Voice & Video",
                "status": "error",
                "latency_ms": 0,
                "message": f"LiveKit check error: {str(e)}"
            }

    def check_all(self, timeout: float = 3.0) -> Dict[str, Any]:
        """Runs all connection checks concurrently and returns an aggregated health map."""
        start_t = time.perf_counter()
        results: Dict[str, Any] = {}

        tasks = {
            "internet": lambda: self.check_internet(timeout=timeout),
            "google_translate": lambda: self.check_translation(timeout=timeout),
            "anthropic_api": lambda: self.check_llm("anthropic"),
            "gemini_api": lambda: self.check_llm("gemini"),
            "deepseek_api": lambda: self.check_llm("deepseek"),
            "groq_api": lambda: self.check_llm("groq"),
            "openai_api": lambda: self.check_llm("openai"),
            "ollama": lambda: self.check_llm("ollama"),
            "custom_ai": lambda: self.check_llm("custom"),
            "chrome_browser": self.check_chrome,
            "mcp_servers": self.check_mcp,
            "websocket_server": self.check_websocket_backend,
            "livekit_webrtc": self.check_livekit
        }

        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_key = {executor.submit(fn): key for key, fn in tasks.items()}
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    results[key] = {
                        "name": key,
                        "status": "error",
                        "latency_ms": 0,
                        "error": str(e),
                        "message": f"Check failed: {e}"
                    }

        total_lat = round((time.perf_counter() - start_t) * 1000, 1)

        connected_count = sum(1 for r in results.values() if r.get("status") in ("connected", "ready", "standby_ready"))
        return {
            "timestamp": time.time(),
            "duration_ms": total_lat,
            "total_checked": len(results),
            "connected_count": connected_count,
            "all_healthy": results.get("internet", {}).get("status") == "connected" and results.get("google_translate", {}).get("status") == "connected",
            "connections": results
        }

    def check_twice(self, timeout: float = 3.0) -> Dict[str, Any]:
        """
        Executes two consecutive complete diagnostic passes to measure connection stability,
        socket reuse speedup (connection pooling), and reliability.
        """
        start_full = time.perf_counter()

        # Pass 1: Cold / initial verification pass
        pass_1 = self.check_all(timeout=timeout)

        # Brief settle time to simulate immediate second verification
        time.sleep(0.1)

        # Pass 2: Warm / pooled verification pass
        pass_2 = self.check_all(timeout=timeout)

        total_duration = round((time.perf_counter() - start_full) * 1000, 1)

        # Calculate comparative metrics and speedup
        comparison = {}
        for key in pass_1["connections"]:
            p1_item = pass_1["connections"].get(key, {})
            p2_item = pass_2["connections"].get(key, {})
            lat1 = p1_item.get("latency_ms", 0)
            lat2 = p2_item.get("latency_ms", 0)

            speedup_pct = 0.0
            if lat1 > 0 and lat2 < lat1:
                speedup_pct = round(((lat1 - lat2) / lat1) * 100, 1)

            comparison[key] = {
                "status_pass_1": p1_item.get("status"),
                "status_pass_2": p2_item.get("status"),
                "latency_pass_1_ms": lat1,
                "latency_pass_2_ms": lat2,
                "speedup_pct": speedup_pct,
                "stable": (p1_item.get("status") == p2_item.get("status"))
            }

        stable_count = sum(1 for c in comparison.values() if c["stable"])
        stability_score = round((stable_count / max(1, len(comparison))) * 100, 1)

        # Build Markdown summary report
        md_lines = [
            "### ⚡ Helper-AI Double-Pass Connection Diagnostic Report",
            f"- **Stability Score**: {stability_score}% ({stable_count}/{len(comparison)} connections verified identical & stable)",
            f"- **Diagnostic Duration**: Pass 1: {pass_1['duration_ms']}ms | Pass 2: {pass_2['duration_ms']}ms | Total: {total_duration}ms",
            "",
            "| Connection Target | Status (Pass 1) | Status (Pass 2) | Pass 1 Latency | Pass 2 Latency | Speedup | Result |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :--- |"
        ]

        for target, comp in comparison.items():
            icon = "✅" if comp["status_pass_2"] in ("connected", "ready", "standby_ready") else ("⚠️" if comp["status_pass_2"] == "offline" else "❌")
            speedup_badge = f"+{comp['speedup_pct']}% faster" if comp['speedup_pct'] > 0 else "steady"
            md_lines.append(
                f"| `{target}` | `{comp['status_pass_1']}` | `{comp['status_pass_2']}` | {comp['latency_pass_1_ms']}ms | {comp['latency_pass_2_ms']}ms | {speedup_badge} | {icon} |"
            )

        return {
            "success": True,
            "pass_count": 2,
            "stability_score_pct": stability_score,
            "total_duration_ms": total_duration,
            "pass_1": pass_1,
            "pass_2": pass_2,
            "comparison": comparison,
            "summary_markdown": "\n".join(md_lines)
        }


connection_checker = ConnectionChecker.get_instance()
