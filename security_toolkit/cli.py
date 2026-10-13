"""Command Line Interface for the Security Auditing and Vulnerability Assessment Toolkit.

Provides a unified terminal CLI for running asynchronous network audits,
OWASP HTTP header security checks, and cryptographic file integrity monitoring.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional

from security_toolkit.port_scanner import AsyncPortScanner
from security_toolkit.header_analyzer import HTTPHeaderSecurityAnalyzer
from security_toolkit.integrity_checker import FileIntegrityChecker
from security_toolkit.reporter import SecurityAuditReporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SecurityToolkit")

ETHICAL_WARNING = """
[!] LEGAL & ETHICAL DISCLAIMER:
    This tool is designed strictly for authorized security auditing, educational labs,
    and self-hosted system hardening. Unauthorized scanning or testing of third-party
    systems without prior written authorization is strictly illegal and unethical.
"""


def parse_ports(port_arg: str) -> List[int]:
    """Parses port ranges (e.g. '80,443' or '80-90' or '22,80-85')."""
    ports = set()
    for part in port_arg.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            ports.update(range(int(start), int(end) + 1))
        elif part.isdigit():
            ports.add(int(part))
    return sorted(list(ports))


def handle_ports(args: argparse.Namespace):
    scanner = AsyncPortScanner(timeout=args.timeout, concurrency=args.concurrency)
    ports = parse_ports(args.ports) if args.ports else None
    logger.info(f"Initiating network audit on {args.host}...")
    res = scanner.scan_sync(args.host, ports=ports)
    print(SecurityAuditReporter.format_text_summary({"port_scan": res}))
    if args.output:
        SecurityAuditReporter.export_json(res, args.output)
        print(f"[+] Results saved to {args.output}")


def handle_headers(args: argparse.Namespace):
    analyzer = HTTPHeaderSecurityAnalyzer(timeout=args.timeout)
    logger.info(f"Auditing HTTP security headers for {args.url}...")
    res = analyzer.analyze(args.url)
    print(SecurityAuditReporter.format_text_summary({"http_headers": res}))
    if args.output:
        SecurityAuditReporter.export_json(res, args.output)
        print(f"[+] Results saved to {args.output}")


def handle_integrity(args: argparse.Namespace):
    fim = FileIntegrityChecker()
    if args.action == "create":
        logger.info(f"Generating cryptographic baseline for {args.dir}...")
        res = fim.create_baseline(args.dir, args.baseline)
        if res.get("success"):
            print(f"[+] Baseline successfully created: {res['baseline_path']} ({res['files_indexed']} files indexed)")
        else:
            print(f"[-] Error: {res.get('error')}")
    elif args.action == "verify":
        logger.info(f"Verifying directory integrity for {args.dir} against baseline...")
        res = fim.verify_integrity(args.dir, args.baseline)
        print(SecurityAuditReporter.format_text_summary({"file_integrity": res}))
        if args.output:
            SecurityAuditReporter.export_json(res, args.output)
            print(f"[+] Results saved to {args.output}")


def handle_full_audit(args: argparse.Namespace):
    combined_report = {}
    if args.host:
        scanner = AsyncPortScanner(timeout=args.timeout)
        combined_report["port_scan"] = scanner.scan_sync(args.host)

    if args.url:
        analyzer = HTTPHeaderSecurityAnalyzer(timeout=args.timeout)
        combined_report["http_headers"] = analyzer.analyze(args.url)

    if args.dir and args.baseline:
        fim = FileIntegrityChecker()
        combined_report["file_integrity"] = fim.verify_integrity(args.dir, args.baseline)

    print(SecurityAuditReporter.format_text_summary(combined_report))
    if args.output:
        SecurityAuditReporter.export_json(combined_report, args.output)
        print(f"[+] Full audit report exported to {args.output}")


def main():
    parser = argparse.ArgumentParser(
        description="Defensive Security Auditing & Vulnerability Assessment Toolkit",
        epilog="Use responsibly and strictly within authorized testing boundaries."
    )
    parser.add_argument("--disclaimer", action="store_true", help="Display full ethical usage guidelines")
    subparsers = parser.add_subparsers(dest="command", help="Auditing modules")

    # 1. Port Scanner
    p_ports = subparsers.add_parser("ports", help="Network port and service auditing")
    p_ports.add_argument("--host", required=True, help="Target hostname or IP address")
    p_ports.add_argument("--ports", help="Port list or range (e.g. '80,443' or '80-100')")
    p_ports.add_argument("--timeout", type=float, default=1.0, help="Connection timeout in seconds")
    p_ports.add_argument("--concurrency", type=int, default=100, help="Concurrent workers")
    p_ports.add_argument("--output", help="Path to save JSON report")

    # 2. HTTP Headers
    p_headers = subparsers.add_parser("headers", help="OWASP HTTP header security evaluation")
    p_headers.add_argument("--url", required=True, help="Target URL (e.g. https://localhost:8000)")
    p_headers.add_argument("--timeout", type=float, default=8.0, help="Request timeout")
    p_headers.add_argument("--output", help="Path to save JSON report")

    # 3. File Integrity Monitoring
    p_fim = subparsers.add_parser("integrity", help="Cryptographic File Integrity Monitoring (FIM)")
    p_fim.add_argument("--action", choices=["create", "verify"], required=True, help="Action to execute")
    p_fim.add_argument("--dir", required=True, help="Target directory to monitor")
    p_fim.add_argument("--baseline", default="baseline.json", help="Path to baseline file")
    p_fim.add_argument("--output", help="Path to save verification report")

    # 4. Full Audit
    p_full = subparsers.add_parser("full-audit", help="Run comprehensive combined security assessment")
    p_full.add_argument("--host", help="Target host for port scan")
    p_full.add_argument("--url", help="Target web URL for header analysis")
    p_full.add_argument("--dir", help="Target directory for integrity check")
    p_full.add_argument("--baseline", help="Baseline path for integrity check")
    p_full.add_argument("--timeout", type=float, default=2.0, help="Network timeout")
    p_full.add_argument("--output", help="Path to save combined JSON report")

    args = parser.parse_args()

    if args.disclaimer or len(sys.argv) == 1:
        print(ETHICAL_WARNING)
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(0)

    if args.command == "ports":
        handle_ports(args)
    elif args.command == "headers":
        handle_headers(args)
    elif args.command == "integrity":
        handle_integrity(args)
    elif args.command == "full-audit":
        handle_full_audit(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
