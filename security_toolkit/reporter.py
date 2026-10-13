"""Security Audit Report Generator supporting JSON, CSV, and Markdown exports."""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List


class SecurityAuditReporter:
    """Exports structured vulnerability and security posture assessment reports."""

    @staticmethod
    def export_json(data: Dict[str, Any], filepath: str) -> str:
        """Saves assessment data to formatted JSON."""
        dest = Path(filepath).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return str(dest)

    @staticmethod
    def export_csv_findings(findings: List[Dict[str, Any]], filepath: str) -> str:
        """Saves security findings list to CSV format."""
        dest = Path(filepath).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not findings:
            with open(dest, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Message"])
                writer.writerow(["No findings recorded."])
            return str(dest)

        fieldnames = list(findings[0].keys())
        with open(dest, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in findings:
                writer.writerow(item)
        return str(dest)

    @staticmethod
    def format_text_summary(report: Dict[str, Any]) -> str:
        """Generates a clean CLI ASCII report compatible with all platform encodings."""
        lines = [
            "============================================================",
            "        [+] DEFENSIVE SECURITY AUDIT ASSESSMENT REPORT      ",
            "============================================================"
        ]

        if "port_scan" in report:
            ps = report["port_scan"]
            lines.append(f"\n[NETWORK AUDIT] Target: {ps.get('host')} ({ps.get('target_ip')})")
            lines.append(f"  * Scanned Ports: {ps.get('scanned_count')} | Open: {ps.get('open_count')} (Duration: {ps.get('elapsed_seconds')}s)")
            for p in ps.get("open_ports", []):
                lines.append(f"    [OPEN] Port {p['port']:<5} [{p['service']}] State: {p['state']}")

        if "http_headers" in report:
            hh = report["http_headers"]
            lines.append(f"\n[HTTP HEADER AUDIT] Target: {hh.get('url')}")
            lines.append(f"  * Score: {hh.get('score')}/100 (Grade: {hh.get('grade')})")
            lines.append(f"  * Present Headers: {hh.get('present_count')} | Missing Defenses: {hh.get('missing_count')}")
            for f in hh.get("findings", []):
                status_tag = f"[{f['status']:<4}]"
                lines.append(f"    {status_tag} {f['header']} ({f.get('severity', 'INFO')})")
                if f.get("recommendation"):
                    lines.append(f"        -> Remediation: {f['recommendation']}")

        if "file_integrity" in report:
            fi = report["file_integrity"]
            lines.append(f"\n[FILE INTEGRITY AUDIT] Status: {fi.get('status')}")
            lines.append(f"  * Verified: {fi.get('unmodified_count')} | Modified: {fi.get('modified_count')} | Added: {fi.get('added_count')} | Deleted: {fi.get('deleted_count')}")
            for mod in fi.get("modified_files", []):
                lines.append(f"    [MODIFIED] {mod['file']}")

        lines.append("\n============================================================")
        lines.append("Notice: Authorized security assessment and diagnostic use only.")
        lines.append("============================================================")
        return "\n".join(lines)
