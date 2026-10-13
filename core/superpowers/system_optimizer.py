"""Superpower System Optimizer & Diagnostics Suite.

Inspects system resources, evaluates memory bottlenecks, detects runaway processes,
tests network latency, and scans for recoverable disk cache.
"""

import os
import psutil
import socket
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


class SuperpowerSystemOptimizer:
    """Introspective PC system optimizer and performance diagnostic suite."""

    @staticmethod
    def get_performance_snapshot() -> Dict[str, Any]:
        """Collects granular hardware, process, and memory telemetry."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        cpu_pct = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count(logical=True)

        # Disk partitions
        disks = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "used_percent": usage.percent
                })
            except Exception:
                pass

        # Top 5 memory-consuming processes
        top_procs = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                info = proc.info
                if info and info['memory_info']:
                    ram_mb = round(info['memory_info'].rss / (1024**2), 1)
                    top_procs.append({
                        "pid": info['pid'],
                        "name": info['name'],
                        "ram_mb": ram_mb
                    })
            except Exception:
                pass

        top_procs.sort(key=lambda x: x["ram_mb"], reverse=True)

        return {
            "timestamp": time.time(),
            "cpu": {
                "usage_percent": cpu_pct,
                "logical_cores": cpu_count
            },
            "memory": {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_percent": mem.percent,
                "swap_used_percent": swap.percent
            },
            "disks": disks,
            "top_memory_consumers": top_procs[:5]
        }

    @staticmethod
    def test_latency(targets: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Tests round-trip TCP connection latency to reliable global gateways."""
        default_targets = [
            ("Cloudflare DNS", "1.1.1.1", 53),
            ("Google DNS", "8.8.8.8", 53),
            ("HTTP Gateway", "www.google.com", 80)
        ]
        results = []
        for name, host, port in default_targets:
            start = time.perf_counter()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2.0)
                sock.connect((host, port))
                sock.close()
                lat_ms = round((time.perf_counter() - start) * 1000, 1)
                results.append({"name": name, "endpoint": f"{host}:{port}", "status": "online", "latency_ms": lat_ms})
            except Exception as e:
                results.append({"name": name, "endpoint": f"{host}:{port}", "status": "unreachable", "error": str(e)})
        return results

    @staticmethod
    def scan_temporary_files(target_dir: str = ".") -> Dict[str, Any]:
        """Scans for safe-to-clean junk files (*.tmp, __pycache__, .pytest_cache)."""
        root_path = Path(target_dir).resolve()
        junk_patterns = ["*.tmp", "*.log", "*.bak"]
        found_files = []
        total_bytes = 0

        for pattern in junk_patterns:
            for p in root_path.rglob(pattern):
                try:
                    if p.is_file():
                        sz = p.stat().st_size
                        found_files.append({"path": str(p.relative_to(root_path)), "size_bytes": sz})
                        total_bytes += sz
                except Exception:
                    pass

        return {
            "scanned_directory": str(root_path),
            "junk_files_count": len(found_files),
            "recoverable_mb": round(total_bytes / (1024**2), 2),
            "files": found_files[:30]
        }
