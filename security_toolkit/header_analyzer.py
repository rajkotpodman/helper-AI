"""HTTP Header Security Analyzer based on OWASP Secure Headers guidelines.

Audits web applications for missing defensive headers, insecure configurations,
and sensitive technology disclosure headers.
"""

from typing import Dict, Any, List, Optional
import requests

RECOMMENDED_SECURITY_HEADERS: Dict[str, Dict[str, Any]] = {
    "Strict-Transport-Security": {
        "severity": "HIGH",
        "description": "Enforces secure (HTTPS) connections and prevents SSL-stripping man-in-the-middle attacks.",
        "recommended_value": "max-age=31536000; includeSubDomains; preload",
        "weight": 25
    },
    "Content-Security-Policy": {
        "severity": "HIGH",
        "description": "Restricts trusted resource origins, mitigating Cross-Site Scripting (XSS) and data injection attacks.",
        "recommended_value": "default-src 'self'; frame-ancestors 'none';",
        "weight": 25
    },
    "X-Frame-Options": {
        "severity": "MEDIUM",
        "description": "Protects against clickjacking attacks by controlling whether the site can be rendered in an iframe.",
        "recommended_value": "DENY or SAMEORIGIN",
        "weight": 15
    },
    "X-Content-Type-Options": {
        "severity": "MEDIUM",
        "description": "Prevents MIME-type sniffing, ensuring browsers strictly honor declared Content-Type.",
        "recommended_value": "nosniff",
        "weight": 15
    },
    "Referrer-Policy": {
        "severity": "LOW",
        "description": "Controls how much referrer information is included with requests when navigating away.",
        "recommended_value": "strict-origin-when-cross-origin or no-referrer",
        "weight": 10
    },
    "Permissions-Policy": {
        "severity": "LOW",
        "description": "Restricts browser feature access (geolocation, camera, microphone, payment APIs).",
        "recommended_value": "geolocation=(), microphone=(), camera=()",
        "weight": 10
    }
}

INFO_DISCLOSURE_HEADERS = [
    "Server",
    "X-Powered-By",
    "X-AspNet-Version",
    "X-AspNetMvc-Version",
    "X-Generator"
]


class HTTPHeaderSecurityAnalyzer:
    """Evaluates HTTP response headers for defensive security posture."""

    def __init__(self, timeout: float = 8.0, verify_ssl: bool = True):
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    def analyze(self, url: str) -> Dict[str, Any]:
        """
        Sends an HTTP GET request to target URL and analyzes returned headers.

        Args:
            url: Target web application URL (e.g. https://example.com).

        Returns:
            Dictionary containing audit scorecard, findings, and remediation advice.
        """
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"

        try:
            headers_req = {
                "User-Agent": "SecurityAuditToolkit/1.0 (Defensive Security Scanner; Lab Environment)"
            }
            resp = requests.get(
                url,
                headers=headers_req,
                timeout=self.timeout,
                verify=self.verify_ssl,
                allow_redirects=True
            )
            raw_headers = dict(resp.headers)
            status_code = resp.status_code
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": f"Failed to retrieve headers from {url}: {str(e)}",
                "findings": []
            }

        findings: List[Dict[str, Any]] = []
        earned_score = 100
        present_security_headers = {}
        missing_security_headers = []

        # 1. Check for missing or present security headers
        for h_name, h_info in RECOMMENDED_SECURITY_HEADERS.items():
            # Check case-insensitively
            matched_val = None
            for k, v in raw_headers.items():
                if k.lower() == h_name.lower():
                    matched_val = v
                    break

            if matched_val:
                present_security_headers[h_name] = matched_val
                findings.append({
                    "header": h_name,
                    "status": "PASS",
                    "severity": "INFO",
                    "value": matched_val,
                    "description": h_info["description"]
                })
            else:
                missing_security_headers.append(h_name)
                earned_score -= h_info["weight"]
                findings.append({
                    "header": h_name,
                    "status": "FAIL",
                    "severity": h_info["severity"],
                    "description": h_info["description"],
                    "recommendation": f"Add '{h_name}: {h_info['recommended_value']}'"
                })

        # 2. Check for information disclosure headers
        disclosed_info = {}
        for h_leak in INFO_DISCLOSURE_HEADERS:
            for k, v in raw_headers.items():
                if k.lower() == h_leak.lower():
                    disclosed_info[k] = v
                    earned_score -= 5
                    findings.append({
                        "header": k,
                        "status": "WARN",
                        "severity": "LOW",
                        "value": v,
                        "description": f"Exposes backend technology stack details ({v}).",
                        "recommendation": f"Suppress or obfuscate the '{k}' header in web server configuration."
                    })

        earned_score = max(0, min(100, earned_score))

        # Assign letter grade
        if earned_score >= 90:
            grade = "A+"
        elif earned_score >= 80:
            grade = "A"
        elif earned_score >= 70:
            grade = "B"
        elif earned_score >= 50:
            grade = "C"
        elif earned_score >= 30:
            grade = "D"
        else:
            grade = "F"

        return {
            "success": True,
            "url": url,
            "status_code": status_code,
            "score": earned_score,
            "grade": grade,
            "present_count": len(present_security_headers),
            "missing_count": len(missing_security_headers),
            "info_leaks_count": len(disclosed_info),
            "raw_headers": raw_headers,
            "findings": findings
        }
