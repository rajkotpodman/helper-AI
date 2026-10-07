"""Runtime Telemetry and Performance Metrics for Helper-AI."""
import time
import psutil
from typing import Dict, Any

class TelemetryCollector:
    """
    Collects real-time operational telemetry, error rates, and tool latencies.
    """
    def __init__(self):
        self.start_time = time.time()
        self.total_goals_started = 0
        self.total_goals_completed = 0
        self.total_goals_failed = 0
        self.tool_invocations: Dict[str, int] = {}
        self.tool_failures: Dict[str, int] = {}
        self.total_latency_ms = 0.0
        self.recorded_calls = 0

    def record_goal_start(self):
        self.total_goals_started += 1

    def record_goal_complete(self, success: bool):
        if success:
            self.total_goals_completed += 1
        else:
            self.total_goals_failed += 1

    def record_tool_call(self, tool_name: str, success: bool, latency_ms: float):
        self.tool_invocations[tool_name] = self.tool_invocations.get(tool_name, 0) + 1
        if not success:
            self.tool_failures[tool_name] = self.tool_failures.get(tool_name, 0) + 1
        self.total_latency_ms += latency_ms
        self.recorded_calls += 1

    def get_snapshot(self) -> Dict[str, Any]:
        """Returns comprehensive telemetry snapshot."""
        uptime_seconds = round(time.time() - self.start_time, 1)
        avg_latency = round(self.total_latency_ms / max(1, self.recorded_calls), 2)
        success_rate = (
            round((self.total_goals_completed / max(1, self.total_goals_started)) * 100, 1)
            if self.total_goals_started > 0 else 100.0
        )

        mem = psutil.virtual_memory()

        return {
            "uptime_seconds": uptime_seconds,
            "goals": {
                "started": self.total_goals_started,
                "completed": self.total_goals_completed,
                "failed": self.total_goals_failed,
                "success_rate_pct": success_rate,
            },
            "tools": {
                "total_invocations": self.recorded_calls,
                "by_tool": self.tool_invocations,
                "failures_by_tool": self.tool_failures,
                "avg_latency_ms": avg_latency,
            },
            "system_telemetry": {
                "cpu_percent": psutil.cpu_percent(interval=None),
                "ram_percent": mem.percent,
                "ram_available_mb": round(mem.available / (1024 * 1024), 1),
            }
        }

# Global singleton
metrics = TelemetryCollector()
