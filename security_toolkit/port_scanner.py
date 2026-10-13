"""Asynchronous Network Port Scanner for Authorized Security Auditing.

Leverages non-blocking asynchronous socket connections to efficiently audit
host accessibility and open network services.
"""

import asyncio
import socket
import time
from typing import List, Dict, Any, Optional

WELL_KNOWN_SERVICES: Dict[int, str] = {
    20: "FTP-Data",
    21: "FTP-Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    135: "MS-RPC",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    1433: "MSSQL",
    1521: "Oracle",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8000: "HTTP-Alt / FastAPi",
    8080: "HTTP-Proxy",
    8443: "HTTPS-Alt",
    9000: "SonarQube / PHP-FPM",
    9200: "Elasticsearch",
    27017: "MongoDB"
}


class AsyncPortScanner:
    """Asynchronous, concurrency-managed network port scanner."""

    def __init__(self, timeout: float = 1.0, concurrency: int = 100):
        """
        Initialize the port scanner.

        Args:
            timeout: Socket connection timeout in seconds.
            concurrency: Maximum simultaneous connection attempts.
        """
        self.timeout = timeout
        self.concurrency = concurrency

    async def check_port(self, host: str, port: int) -> Dict[str, Any]:
        """
        Asynchronously tests connectivity to a single TCP port.

        Args:
            host: Target hostname or IP address.
            port: Target port number.

        Returns:
            Dictionary with port status and service description.
        """
        service = WELL_KNOWN_SERVICES.get(port, "Unknown")
        try:
            conn = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(conn, timeout=self.timeout)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            return {
                "port": port,
                "state": "open",
                "service": service,
                "banner": None
            }
        except (asyncio.TimeoutError, TimeoutError):
            return {
                "port": port,
                "state": "filtered / timeout",
                "service": service,
                "banner": None
            }
        except (ConnectionRefusedError, OSError):
            return {
                "port": port,
                "state": "closed",
                "service": service,
                "banner": None
            }
        except Exception as e:
            return {
                "port": port,
                "state": f"error: {str(e)[:30]}",
                "service": service,
                "banner": None
            }

    async def scan(
        self,
        host: str,
        ports: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Scans a specified list of ports against the target host.

        Args:
            host: Hostname or IP to scan.
            ports: List of port numbers to check. Defaults to common service ports.

        Returns:
            Dictionary containing audit results, duration, and open port summaries.
        """
        # Resolve target IP
        try:
            target_ip = socket.gethostbyname(host)
        except socket.gaierror as e:
            return {
                "success": False,
                "host": host,
                "error": f"Failed to resolve host '{host}': {str(e)}",
                "open_ports": [],
                "scanned_count": 0
            }

        ports_to_scan = ports or sorted(list(WELL_KNOWN_SERVICES.keys()))
        semaphore = asyncio.Semaphore(self.concurrency)
        start_time = time.perf_counter()

        async def _bounded_check(p: int):
            async with semaphore:
                return await self.check_port(target_ip, p)

        tasks = [_bounded_check(p) for p in ports_to_scan]
        results = await asyncio.gather(*tasks)

        elapsed = round(time.perf_counter() - start_time, 2)
        open_ports = [r for r in results if r["state"] == "open"]

        return {
            "success": True,
            "host": host,
            "target_ip": target_ip,
            "scanned_count": len(ports_to_scan),
            "open_count": len(open_ports),
            "elapsed_seconds": elapsed,
            "open_ports": open_ports,
            "all_results": results
        }

    def scan_sync(
        self,
        host: str,
        ports: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Synchronous wrapper for execution in non-async contexts."""
        return asyncio.run(self.scan(host, ports))
