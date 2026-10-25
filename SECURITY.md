# Security Policy & Architecture

The **Helper-AI** team is committed to delivering a secure, reliable autonomous execution environment. Because Helper-AI executes real operating system commands, interacts with live internet services, and manipulates files on the host computer, security is treated as an architectural foundational pillar.

---

## 🛡️ Supported Versions

| Version | Status | Security Patches |
| :--- | :--- | :--- |
| **2.9.x** | **Active / Current** | :white_check_mark: Full Support |
| **2.8.x** | **Maintenance** | :white_check_mark: Full Support |
| **2.7.x** | **Maintenance** | :white_check_mark: Critical Security Only |
| **2.0.x** | **Deprecated** | :x: Upgrade to 2.9.x Recommended |
| **1.x** | **Deprecated** | :x: Upgrade to 2.9.x Recommended |

---

## 🔒 Threat Model & Defensive Controls

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        THREAT VECTOR & DEFENSE MATRIX                  │
├─────────────────────────┬──────────────────────────┬───────────────────┤
│ Threat Vector           │ Potential Impact         │ Defensive Control │
├─────────────────────────┼──────────────────────────┼───────────────────┤
│ Malicious Prompt /      │ Unauthorized shell       │ Safe Mode AST /   │
│ Prompt Injection        │ command execution        │ Blocklist regex   │
├─────────────────────────┼──────────────────────────┼───────────────────┤
│ Destructive File Ops    │ Overwriting system files │ Scope constraint  │
│ (Path Traversal)        │ (/etc/passwd, C:\Windows)│ & Path resolution │
├─────────────────────────┼──────────────────────────┼───────────────────┤
│ Unintended Social Posts │ Public reputation damage │ 1-Click HITL      │
│                         │ or spam generation       │ Approval Gates    │
├─────────────────────────┼──────────────────────────┼───────────────────┤
│ Secret Exposure in Logs │ API Key / Credential leak│ Secret Redaction  │
│                         │ via telemetry/audit      │ in AuditLogger    │
└─────────────────────────┴──────────────────────────┴───────────────────┘
```

### 1. Safe Mode Enforcement
When `SAFE_MODE=true` is enabled in configuration or `.env`:
- **Destructive Commands Blocked:** Commands containing destructive patterns (e.g. `rmdir /s /q`, `Format-Volume`, `del /f /s /q C:\*`, `sudo rm -rf /`, `mkfs`, fork bombs) are immediately halted and rejected before shell evaluation.
- **Root/Admin Restraints:** Agent drops privileges or refuses to run commands with elevated administrative permissions without explicit user authorization.

### 2. Human-in-the-Loop (HITL) Authorization
For sensitive tasks—including external social media publishing, permanent process termination, network configuration changes, and script execution:
- The execution loop yields execution and registers a pending permission record in `PermissionManager`.
- The user is presented with a non-technical approval prompt via the Web Dashboard (or API `/api/permission/respond`).
- Actions timeout automatically if not approved within a configurable window (default: 60 seconds), defaulting to safe rejection.

### 3. Automated Secret Masking & Audit Logging
All interactions, tool calls, and LLM completions are recorded in structured JSONL format (`logs/audit.jsonl`):
- API keys (OpenAI, Gemini, Groq, Anthropic), Bearer tokens, private paths, and basic auth headers are automatically pattern-matched and replaced with `[REDACTED_SECRET]`.
- Audit logs provide an immutable timeline of operations for compliance and security forensics.

### 4. Container Isolation
When deployed via Docker:
- Helper-AI runs inside an unprivileged user space.
- Host filesystem mounts are strictly confined to designated volumes (`./logs`, `./history`, `./downloads`).
- Host processes and administrative subnets remain isolated.

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT open a public GitHub issue or discussion.**
2. **Email your advisory to:** `athanu000@gmail.com`
3. **Include the following information:**
   - Detailed description of the vulnerability and attack vector.
   - Exact steps or script to reproduce the issue.
   - Affected versions and environments (Windows, Linux, Docker).
   - Potential impact and suggested mitigations.
4. **Response Timelines:**
   - **Initial acknowledgment:** Within 24-48 hours.
   - **Triage & reproduction:** Within 3-5 business days.
   - **Security patch release:** Coordinated disclosure within 14 days of verification.

We appreciate the security research community's efforts to keep Helper-AI safe for all users.
