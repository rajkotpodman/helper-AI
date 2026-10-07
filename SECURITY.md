# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Architecture & Threat Model

Helper-AI executes commands and operates files on the host computer. To ensure enterprise security:
1. **Safe Mode Enforcement:** Blocks destructive commands (e.g. recursive disk format, sensitive registry edits).
2. **Audit Logging:** Every tool call and parameter set is captured in `logs/audit.jsonl` with API keys and sensitive tokens automatically redacted.
3. **Environment Isolation:** Containerized deployments run inside unprivileged Linux containers.

## Reporting a Vulnerability

If you discover a security vulnerability in Helper-AI, please report it responsibly:
1. Do **NOT** disclose vulnerabilities in public GitHub issues or discussions.
2. Email the maintainer at `athanu000@gmail.com` with:
   - A description of the issue.
   - Proof of concept reproduction steps.
   - Potential impact.
3. You will receive an acknowledgment within 48 hours and updates until the patch is released.
