#!/usr/bin/env python3
"""
PHP Universal Vaccine - Online Vulnerability & Immunization Scanner
===================================================================
Remotely scans any live web domain to check if the PHP Universal Security Vaccine
is active and assesses immunization posture against critical PHP CVEs.

Usage:
  python3 scripts/online_scanner.py https://your-website.com
  python3 scripts/online_scanner.py --json https://your-website.com
"""

import sys
import json
import argparse
import urllib.request
import urllib.error
from urllib.parse import urlparse, urljoin

PROBES = [
    {
        "name": "CVE-2024-4577 / CVE-2012-1823 (CGI Argument Injection)",
        "query": "%ad-d+allow_url_include%3d1",
        "expected_code": 403,
        "criticality": "CRITICAL"
    },
    {
        "name": "PHP Object Injection / Deserialization Gadget",
        "query": "vaccine_test=O%3A8%3A%22stdClass%22%3A1%3A%7Bs%3A4%3A%22test%22%3Bs%3A4%3A%22hack%22%3B%7D",
        "expected_code": 403,
        "criticality": "CRITICAL"
    },
    {
        "name": "Arbitrary Stream Wrapper (php://input)",
        "query": "include=php%3A%2F%2Finput",
        "expected_code": 403,
        "criticality": "HIGH"
    },
    {
        "name": "Path Traversal & Truncation Sequence",
        "query": "page=..%2F..%2F..%2Fetc%2Fpasswd",
        "expected_code": 403,
        "criticality": "HIGH"
    },
    {
        "name": "High-Confidence SQL Injection Probe",
        "query": "id=-1+UNION+ALL+SELECT+1%2C2%2C3--",
        "expected_code": 403,
        "criticality": "HIGH"
    }
]

def scan_target(target_url: str) -> dict:
    parsed = urlparse(target_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Invalid target URL. Must include scheme, e.g. https://example.com")

    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    print(f"[*] Initiating Remote Security & Immunization Scan: {base_url}")

    results = []
    points = 100
    vaccine_detected = False

    # 1. Baseline Request & Header Inspection
    req = urllib.request.Request(
        base_url,
        headers={"User-Agent": "PHP-Universal-Vaccine-Scanner/1.3"}
    )
    headers = {}
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            headers = dict(resp.headers)
    except urllib.error.HTTPError as e:
        headers = dict(e.headers)
    except Exception as e:
        print(f"[!] Target unreachable: {e}")
        return {"error": str(e), "target": target_url}

    # Check Vaccine Headers
    if "X-Protected-By" in headers or "X-Immunized-By" in headers:
        vaccine_detected = True
        vaccine_version = headers.get("X-Protected-By", headers.get("X-Immunized-By", "Unknown"))
    else:
        vaccine_version = "None"
        points -= 20

    # Check Standard Security Headers
    has_nosniff = "X-Content-Type-Options" in headers
    has_frame_options = "X-Frame-Options" in headers
    if not has_nosniff: points -= 5
    if not has_frame_options: points -= 5

    # 2. Run Non-Destructive Threat Probes
    for p in PROBES:
        probe_url = f"{base_url}?{p['query']}"
        probe_req = urllib.request.Request(
            probe_url,
            headers={"User-Agent": "PHP-Universal-Vaccine-Scanner/1.3"}
        )
        try:
            with urllib.request.urlopen(probe_req, timeout=10) as resp:
                code = resp.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception:
            code = 0

        blocked = (code == p["expected_code"])
        if not blocked:
            if p["criticality"] == "CRITICAL":
                points -= 25
            else:
                points -= 10

        results.append({
            "probe_name": p["name"],
            "criticality": p["criticality"],
            "http_status_code": code,
            "blocked_with_403": blocked
        })

    # 3. Calculate Grade
    points = max(0, min(100, points))
    if points >= 95: grade = "A+"
    elif points >= 85: grade = "A"
    elif points >= 75: grade = "B"
    elif points >= 60: grade = "C"
    elif points >= 45: grade = "D"
    else: grade = "F"

    return {
        "target": target_url,
        "security_score": points,
        "security_grade": grade,
        "vaccine_detected": vaccine_detected,
        "vaccine_version": vaccine_version,
        "security_headers": {
            "x_content_type_options": has_nosniff,
            "x_frame_options": has_frame_options
        },
        "probe_results": results,
        "remediation_cmd": "curl -sSL https://raw.githubusercontent.com/ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL/main/scripts/inoculate.sh | sudo bash"
    }

def print_report(scan_res: dict):
    if "error" in scan_res:
        print(f"[!] Scan Error: {scan_res['error']}")
        return

    print("==================================================================")
    print("      PHP UNIVERSAL VACCINE: LIVE ONLINE SECURITY REPORT         ")
    print("==================================================================")
    print(f" Target Domain:      {scan_res['target']}")
    print(f" Overall Grade:      {scan_res['security_grade']} ({scan_res['security_score']}/100)")
    print(f" Inoculation Status: {'IMMUNIZED' if scan_res['vaccine_detected'] else 'UNPROTECTED / VULNERABLE'}")
    print(f" Engine Version:     {scan_res['vaccine_version']}")
    print("------------------------------------------------------------------")
    print(" Exploit Probe Results:")
    for r in scan_res["probe_results"]:
        status = "[BLOCKED - 403]" if r["blocked_with_403"] else f"[VULNERABLE - HTTP {r['http_status_code']}]"
        print(f"  * {r['probe_name']}: {status}")
    print("------------------------------------------------------------------")
    if not scan_res["vaccine_detected"] or scan_res["security_score"] < 90:
        print(" [!] REMEDIATION REQUIRED: To immediately immunize this server:")
        print(f"     {scan_res['remediation_cmd']}")
    else:
        print(" [+] EXCELLENT: Target is fully immunized by the PHP Universal Vaccine.")
    print("==================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PHP Universal Vaccine Online Scanner")
    parser.add_argument("url", nargs="?", default="http://localhost", help="Target URL to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    res = scan_target(args.url)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print_report(res)
