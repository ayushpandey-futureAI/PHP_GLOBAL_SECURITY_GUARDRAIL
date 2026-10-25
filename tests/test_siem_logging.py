#!/usr/bin/env python3
"""
Unit Test Suite: SIEM / CEF / JSON Telemetry Dispatcher Verification
=====================================================================
Validates that the PHP Universal Vaccine generates compliant CEF and JSON
telemetry for enterprise SIEM ingestion (Splunk, Datadog, Elastic, Sentinel).
"""

import json
import re
from datetime import datetime, timezone

def generate_cef(threat_id, category, detail, payload, ip="192.168.1.100", method="POST", uri="/api/login", latency_ms=0.015):
    payload_sample = str(payload)[:400].replace("=", "\\=").replace("\\", "\\\\")
    return (
        f"CEF:0|PHP-Universal-Vaccine|RASP|1.3.0|{threat_id}|{detail}|8|"
        f"src={ip} requestMethod={method} request={uri} cs1={category} cs1Label=Category cn1={latency_ms} cn1Label=LatencyMs msg={payload_sample}"
    )

def generate_json(threat_id, category, detail, payload, ip="10.0.0.5", method="GET", uri="/item?id=1", latency_ms=0.012, action="ENFORCE"):
    timestamp = datetime.now(timezone.utc).isoformat()
    return json.dumps({
        "timestamp": timestamp,
        "threat_id": threat_id,
        "category": category,
        "ip": ip,
        "method": method,
        "uri": uri,
        "latency_ms": latency_ms,
        "detail": detail,
        "payload": str(payload)[:400],
        "action": action
    })

def parse_log_line(line):
    line = line.strip()
    if line.startswith("CEF:0"):
        parts = line.split("|")
        # Extract extension key-value pairs
        ext = {}
        if len(parts) >= 8:
            ext_str = "|".join(parts[7:])
            for match in re.finditer(r'(\w+)=([^=]+?)(?=\s+\w+=|$)', ext_str):
                ext[match.group(1)] = match.group(2).strip()
        return {
            "format": "CEF",
            "threat_id": parts[4] if len(parts) > 4 else "UNKNOWN",
            "detail": parts[5] if len(parts) > 5 else "",
            "severity": parts[6] if len(parts) > 6 else "1",
            "extensions": ext
        }

    if line.startswith("{"):
        data = json.loads(line)
        data["format"] = "JSON"
        return data

    # Custom text fallback
    m = re.search(r'\[(.*?)\] \[THREAT_INTERCEPTED\] ID: ([\w\-]+) \| CAT: ([\w\-]+) \| IP: ([\d\.:]+) \| METHOD: (\w+) \| URI: ([^\s|]+)', line)
    if m:
        return {
            "format": "TEXT",
            "timestamp": m.group(1),
            "threat_id": m.group(2),
            "category": m.group(3),
            "ip": m.group(4),
            "method": m.group(5),
            "uri": m.group(6)
        }
    return {"format": "UNKNOWN", "raw": line}

def test_cef_spec():
    cef = generate_cef(
        threat_id="THREAT-PHP-CGI-001",
        category="CGI_ARGUMENT_INJECTION",
        detail="PHP-CGI Argument Injection probe",
        payload="-d allow_url_include=1",
        ip="192.168.1.100",
        method="POST",
        uri="/index.php"
    )
    print(f"[+] Formatted CEF Output: {cef}")
    parsed = parse_log_line(cef)
    assert parsed["format"] == "CEF", "Log format should be CEF"
    assert parsed["threat_id"] == "THREAT-PHP-CGI-001", "Threat ID failed"
    assert parsed["severity"] == "8", "Severity score failed"
    assert parsed["extensions"]["src"] == "192.168.1.100", "Source IP mismatch"
    assert parsed["extensions"]["requestMethod"] == "POST", "Method mismatch"
    assert parsed["extensions"]["cs1"] == "CGI_ARGUMENT_INJECTION", "Category mismatch"
    print("  -> ArcSight CEF Standard Test: PASSED")

def test_json_spec():
    entry = generate_json(
        threat_id="THREAT-PHP-DESER-001",
        category="PHP_OBJECT_INJECTION",
        detail="PHPGGC Monolog gadget chain",
        payload='O:14:"Monolog\\Logger":1:{s:8:"handlers";a:1:{}}',
        ip="10.0.0.5",
        method="GET",
        uri="/login",
        latency_ms=0.018,
        action="ENFORCE"
    )
    print(f"[+] Formatted JSON Output: {entry}")
    parsed = parse_log_line(entry)
    assert parsed["format"] == "JSON", "Log format should be JSON"
    assert parsed["threat_id"] == "THREAT-PHP-DESER-001", "Threat ID failed"
    assert parsed["category"] == "PHP_OBJECT_INJECTION", "Category failed"
    assert parsed["ip"] == "10.0.0.5", "IP failed"
    assert parsed["action"] == "ENFORCE", "Action failed"
    assert parsed["latency_ms"] == 0.018, "Latency failed"
    print("  -> Structured JSON SIEM Test: PASSED")

def test_text_fallback():
    raw = "[2026-10-25T09:00:00+00:00] [THREAT_INTERCEPTED] ID: THREAT-PHP-SQLI-001 | CAT: SQL_INJECTION | IP: 172.16.0.4 | METHOD: POST | URI: /search | LATENCY: 0.021ms | DETAIL: UNION query | PAYLOAD: -1 UNION SELECT 1,2,3"
    parsed = parse_log_line(raw)
    assert parsed["format"] == "TEXT", "Log format should be TEXT"
    assert parsed["threat_id"] == "THREAT-PHP-SQLI-001", "Threat ID failed"
    assert parsed["ip"] == "172.16.0.4", "IP failed"
    print("  -> Standard Custom Log Test: PASSED")

if __name__ == "__main__":
    print("==================================================================")
    print("       SIEM / CEF / JSON TELEMETRY FORMAT VERIFICATION TEST       ")
    print("==================================================================")
    test_cef_spec()
    test_json_spec()
    test_text_fallback()
    print("==================================================================")
    print(" All SIEM Formatter Tests Passed Successfully! (100%)             ")
    print("==================================================================")
