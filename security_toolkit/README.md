# 🛡️ Defensive Security Auditing & Vulnerability Assessment Toolkit

A modular, robust, and extensible Python toolkit built for authorized security auditing, system hardening diagnostics, and educational laboratory environments.

---

## ⚖️ Ethical & Legal Disclaimer

> **IMPORTANT NOTICE:**  
> This toolkit is strictly intended for **authorized penetration testing**, **educational test labs**, and **self-hosted infrastructure auditing**.  
> Scanning or evaluating network hosts, web applications, or systems without prior written authorization from the system owner is illegal and unethical under computer crime laws (e.g., US CFAA, UK Computer Misuse Act, Indian IT Act).  
> The authors and maintainers assume no liability for misuse of this software. Always test responsibly in isolated or owned lab environments.

---

## 💡 What Does This Toolkit Do? (Simple Explanation for Everyone)

- **Network Port Scanner (`ports`):** Think of network ports like numbered doors on your computer (like Door 80 for websites, Door 22 for remote logins). The port scanner checks which "doors" are currently open so you know if any unnecessary services are exposed.
- **HTTP Header Analyzer (`headers`):** When your web browser talks to a website, the website sends back security instructions called "headers" (like: *"don't let anyone frame this site"* or *"only use HTTPS"*). This tool inspects those headers, gives the site a security score (0 to 100%), and gives a letter grade from A+ down to F.
- **File Integrity Monitor (`integrity`):** Computes a unique digital fingerprint (SHA-256 hash) for every file in a folder. If any file is secretly changed, added, or deleted, this tool immediately sounds an alarm and tells you exactly which file was altered.

---

## 📦 Architecture & Core Modules

The toolkit is organized into modular components adhering to clean object-oriented principles, asynchronous I/O, and type hints:

```
security_toolkit/
├── __init__.py               # Package exports & versioning
├── port_scanner.py          # Asynchronous socket-based TCP port scanner
├── header_analyzer.py        # OWASP-aligned HTTP security header evaluator & scorecard
├── integrity_checker.py      # Cryptographic SHA-256 File Integrity Monitor (FIM)
├── reporter.py               # JSON, CSV, and formatted ASCII terminal report exporter
├── cli.py                    # Unified CLI with subcommands & argument parser
└── README.md                 # Complete documentation & test lab guidelines
```

### 1. `AsyncPortScanner` (`port_scanner.py`)
- **Non-blocking Concurrency**: Uses Python's native `asyncio.open_connection` with `asyncio.Semaphore` to audit hundreds of ports concurrently without exhausting operating system file descriptors.
- **Port Mapping**: Built-in mapping of 25+ standard services (SSH, HTTP, HTTPS, MySQL, Redis, FastApi, etc.).
- **Graceful Error Handling**: Robust timeout classification distinguishing open, closed, and filtered/timeout states.
- **Synchronous Bridge**: Includes `scan_sync()` for seamless CLI and scripted execution.

### 2. `HTTPHeaderSecurityAnalyzer` (`header_analyzer.py`)
- **OWASP Best Practices**: Assesses critical defensive headers:
  - `Strict-Transport-Security` (HSTS - 25 pts)
  - `Content-Security-Policy` (CSP - 25 pts)
  - `X-Frame-Options` (Clickjacking mitigation - 15 pts)
  - `X-Content-Type-Options` (MIME-sniffing prevention - 15 pts)
  - `Referrer-Policy` (10 pts)
  - `Permissions-Policy` (10 pts)
- **Technology Leakage Detection**: Detects information disclosure headers (`Server`, `X-Powered-By`, `X-AspNet-Version`, etc.) and applies score penalties.
- **Scoring & Letter Grading**: Computes an overall hardening score (0–100%) and grades the target from `A+` down to `F`.

### 3. `FileIntegrityChecker` (`integrity_checker.py`)
- **Cryptographic Hashing**: Chunked 64 KB SHA-256 reads for efficient, low-memory baseline generation across large file structures.
- **Drift & Tamper Detection**: Compares current directory trees against baseline snapshots, detecting:
  - Unauthorized modifications (hash mismatch)
  - Added files (potential backdoors or unapproved drops)
  - Deleted critical configuration files

### 4. `SecurityAuditReporter` (`reporter.py`)
- **Multi-Format Export**: Generates machine-readable JSON for CI/CD or SIEM ingestion, structured CSV findings lists, and clean ASCII terminal summaries.

---

## 🚀 Installation & Requirements

Requires **Python 3.10+**.

```bash
# Clone or navigate to the repository
cd "e:/ai agent"

# Install dependencies
pip install requests pytest pytest-asyncio
```

---

## 💻 CLI Usage Guide

The CLI supports unified subcommands: `ports`, `headers`, `integrity`, and `full-audit`.

### 1. Display Ethical Notice
```bash
python -m security_toolkit.cli --disclaimer
```

### 2. Network Port Scanner
Scan localhost or authorized internal lab servers:
```bash
# Scan default well-known services on localhost
python -m security_toolkit.cli ports --host 127.0.0.1

# Scan specific ports or port ranges with custom timeout and concurrency
python -m security_toolkit.cli ports --host 127.0.0.1 --ports 80,443,8000-8080 --timeout 0.5 --concurrency 50

# Save output to JSON
python -m security_toolkit.cli ports --host 127.0.0.1 --ports 8000,8080 --output port_audit.json
```

### 3. HTTP Header Security Audit
Audit local or self-hosted web applications:
```bash
# Analyze local dev server
python -m security_toolkit.cli headers --url http://127.0.0.1:8000

# Analyze public test endpoint and save findings
python -m security_toolkit.cli headers --url https://example.com --output header_audit.json
```

### 4. File Integrity Monitoring (FIM)
Create a baseline of sensitive configuration files and verify integrity:
```bash
# Step 1: Create cryptographic baseline snapshot
python -m security_toolkit.cli integrity --action create --dir ./config --baseline ./config_baseline.json

# Step 2: Verify integrity against baseline (detect modifications/additions/deletions)
python -m security_toolkit.cli integrity --action verify --dir ./config --baseline ./config_baseline.json --output fim_report.json
```

### 5. Full Combined Security Assessment
Execute a single consolidated audit across ports, web headers, and file integrity:
```bash
python -m security_toolkit.cli full-audit \
  --host 127.0.0.1 \
  --url http://127.0.0.1:8000 \
  --dir ./config \
  --baseline ./config_baseline.json \
  --output full_audit_report.json
```

---

## 🧪 Automated Testing

Run the automated test suite with pytest:

```bash
pytest tests/test_security_toolkit.py -v
```

All 13 unit and integration tests validate:
- Asynchronous socket connections and timeouts
- OWASP header scoring and information disclosure penalties
- Baseline creation and drift detection (modifications, additions, deletions)
- JSON and CSV reporting integrity
- CLI port range parsing logic
