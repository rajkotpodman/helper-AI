"""Comprehensive Unit & Integration Tests for Security Auditing Toolkit.

Covers:
- AsyncPortScanner (concurrency, port testing, DNS resolution error handling)
- HTTPHeaderSecurityAnalyzer (OWASP scoring, missing headers, info disclosure, grade computation)
- FileIntegrityChecker (SHA-256 calculation, baseline creation, tamper detection, additions/deletions)
- SecurityAuditReporter (JSON serialization, CSV findings export, ASCII report generation)
- CLI Argument Helpers (port range parser)
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from security_toolkit.port_scanner import AsyncPortScanner, WELL_KNOWN_SERVICES
from security_toolkit.header_analyzer import HTTPHeaderSecurityAnalyzer, RECOMMENDED_SECURITY_HEADERS
from security_toolkit.integrity_checker import FileIntegrityChecker
from security_toolkit.reporter import SecurityAuditReporter
from security_toolkit.cli import parse_ports


# ============================================================================
# 1. Port Scanner Tests
# ============================================================================

def test_port_scanner_initialization():
    scanner = AsyncPortScanner(timeout=0.5, concurrency=50)
    assert scanner.timeout == 0.5
    assert scanner.concurrency == 50


@pytest.mark.asyncio
async def test_port_scanner_single_port_closed():
    # Scanning a port that is typically closed or reserved locally
    scanner = AsyncPortScanner(timeout=0.1)
    # Using 127.0.0.1 on a port unlikely to be open
    result = await scanner.check_port("127.0.0.1", 65530)
    assert result["port"] == 65530
    assert result["state"] in ["closed", "filtered / timeout"]


@pytest.mark.asyncio
async def test_port_scanner_resolution_failure():
    scanner = AsyncPortScanner(timeout=0.2)
    result = await scanner.scan("non-existent-domain-for-testing-12345.local", ports=[80])
    assert result["success"] is False
    assert "Failed to resolve host" in result["error"]


def test_port_scanner_sync_wrapper():
    scanner = AsyncPortScanner(timeout=0.2, concurrency=5)
    result = scanner.scan_sync("127.0.0.1", ports=[80, 443])
    assert result["success"] is True
    assert result["scanned_count"] == 2
    assert "elapsed_seconds" in result


# ============================================================================
# 2. HTTP Header Security Analyzer Tests
# ============================================================================

def test_header_analyzer_perfect_score():
    analyzer = HTTPHeaderSecurityAnalyzer()

    # Mock response with all recommended security headers and no leak headers
    mock_headers = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Content-Security-Policy": "default-src 'self'",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=()"
    }

    mock_resp = MagicMock()
    mock_resp.headers = mock_headers
    mock_resp.status_code = 200

    with patch("requests.get", return_value=mock_resp):
        report = analyzer.analyze("https://secure-app.internal")

    assert report["success"] is True
    assert report["score"] == 100
    assert report["grade"] == "A+"
    assert report["missing_count"] == 0
    assert report["present_count"] == 6


def test_header_analyzer_missing_headers_and_leaks():
    analyzer = HTTPHeaderSecurityAnalyzer()

    # Response with missing headers and technology disclosure
    mock_headers = {
        "Server": "Apache/2.4.41 (Ubuntu)",
        "X-Powered-By": "PHP/7.4.3"
    }

    mock_resp = MagicMock()
    mock_resp.headers = mock_headers
    mock_resp.status_code = 200

    with patch("requests.get", return_value=mock_resp):
        report = analyzer.analyze("http://insecure-app.internal")

    assert report["success"] is True
    assert report["score"] < 50
    assert report["grade"] in ["D", "F"]
    assert report["missing_count"] == len(RECOMMENDED_SECURITY_HEADERS)
    assert report["info_leaks_count"] == 2


def test_header_analyzer_connection_failure():
    analyzer = HTTPHeaderSecurityAnalyzer()

    with patch("requests.get", side_effect=Exception("Connection refused")):
        report = analyzer.analyze("https://unreachable-endpoint.local")

    assert report["success"] is False
    assert "Failed to retrieve headers" in report["error"]


# ============================================================================
# 3. File Integrity Monitoring (FIM) Tests
# ============================================================================

def test_file_integrity_baseline_and_verification(tmp_path):
    fim = FileIntegrityChecker()

    # Setup temporary directory with test files
    test_dir = tmp_path / "protected_configs"
    test_dir.mkdir()
    (test_dir / "nginx.conf").write_text("server { listen 80; }", encoding="utf-8")
    (test_dir / "app.env").write_text("DEBUG=False\nPORT=8080", encoding="utf-8")

    baseline_file = tmp_path / "baseline.json"

    # 1. Create Baseline
    base_res = fim.create_baseline(str(test_dir), str(baseline_file))
    assert base_res["success"] is True
    assert base_res["files_indexed"] == 2
    assert baseline_file.exists()

    # 2. Verify Untouched State
    verify_res = fim.verify_integrity(str(test_dir), str(baseline_file))
    assert verify_res["success"] is True
    assert verify_res["has_violations"] is False
    assert verify_res["unmodified_count"] == 2
    assert verify_res["modified_count"] == 0
    assert verify_res["added_count"] == 0
    assert verify_res["deleted_count"] == 0

    # 3. Modify a file
    (test_dir / "app.env").write_text("DEBUG=True\nPORT=9999", encoding="utf-8")
    verify_modified = fim.verify_integrity(str(test_dir), str(baseline_file))
    assert verify_modified["has_violations"] is True
    assert verify_modified["modified_count"] == 1
    assert verify_modified["modified_files"][0]["file"] == "app.env"

    # 4. Add a new unauthorized file
    (test_dir / "backdoor.py").write_text("print('rogue code')", encoding="utf-8")
    verify_added = fim.verify_integrity(str(test_dir), str(baseline_file))
    assert verify_added["has_violations"] is True
    assert verify_added["added_count"] == 1
    assert "backdoor.py" in verify_added["added_files"]

    # 5. Delete a file
    (test_dir / "nginx.conf").unlink()
    verify_deleted = fim.verify_integrity(str(test_dir), str(baseline_file))
    assert verify_deleted["has_violations"] is True
    assert verify_deleted["deleted_count"] == 1
    assert "nginx.conf" in verify_deleted["deleted_files"]


def test_file_integrity_missing_directory():
    fim = FileIntegrityChecker()
    res = fim.create_baseline("non_existent_folder_xyz123", "baseline.json")
    assert res["success"] is False
    assert "does not exist" in res["error"]


def test_file_integrity_missing_baseline(tmp_path):
    fim = FileIntegrityChecker()
    res = fim.verify_integrity(str(tmp_path), str(tmp_path / "missing_base.json"))
    assert res["success"] is False
    assert "Baseline file not found" in res["error"]


# ============================================================================
# 4. Reporter Tests
# ============================================================================

def test_reporter_json_and_csv(tmp_path):
    reporter = SecurityAuditReporter()
    sample_data = {
        "assessment": "network",
        "open_ports": [80, 443]
    }
    json_path = tmp_path / "report.json"
    reporter.export_json(sample_data, str(json_path))
    assert json_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["assessment"] == "network"

    findings = [
        {"header": "HSTS", "status": "FAIL", "severity": "HIGH"},
        {"header": "CSP", "status": "PASS", "severity": "INFO"}
    ]
    csv_path = tmp_path / "findings.csv"
    reporter.export_csv_findings(findings, str(csv_path))
    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8")
    assert "HSTS" in content
    assert "CSP" in content


def test_reporter_text_summary():
    report = {
        "port_scan": {
            "host": "localhost",
            "target_ip": "127.0.0.1",
            "scanned_count": 2,
            "open_count": 1,
            "elapsed_seconds": 0.05,
            "open_ports": [{"port": 80, "service": "HTTP", "state": "open"}]
        },
        "http_headers": {
            "url": "https://localhost:8000",
            "score": 85,
            "grade": "A",
            "present_count": 5,
            "missing_count": 1,
            "findings": [{"header": "HSTS", "status": "FAIL", "severity": "HIGH", "recommendation": "Add HSTS"}]
        },
        "file_integrity": {
            "status": "COMPROMISED / DRIFTED",
            "unmodified_count": 10,
            "modified_count": 1,
            "added_count": 0,
            "deleted_count": 0,
            "modified_files": [{"file": "config.json"}]
        }
    }
    summary = SecurityAuditReporter.format_text_summary(report)
    assert "[NETWORK AUDIT]" in summary
    assert "[HTTP HEADER AUDIT]" in summary
    assert "[FILE INTEGRITY AUDIT]" in summary
    assert "Port 80" in summary
    assert "Score: 85/100" in summary
    assert "[MODIFIED] config.json" in summary


# ============================================================================
# 5. CLI Helpers
# ============================================================================

def test_parse_ports():
    assert parse_ports("80,443") == [80, 443]
    assert parse_ports("80-83") == [80, 81, 82, 83]
    assert parse_ports("22, 80-82, 443") == [22, 80, 81, 82, 443]
