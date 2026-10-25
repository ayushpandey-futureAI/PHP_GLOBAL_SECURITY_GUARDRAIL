#!/usr/bin/env python3
"""
Dynamic EPSS & CVSS Risk Calibration Engine
============================================
Calculates composite threat weights combining FIRST.org EPSS exploit
probability and CVSS v4.0 impact to optimize RASP enforcement policies.
"""

import json
from pathlib import Path

SIGNATURES_FILE = Path(__file__).parent / "../../schema/threat_signatures.json"

def calibrate_threat_matrix(signatures_path=SIGNATURES_FILE):
    with open(signatures_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    signatures = data.get("signatures", [])
    calibrated_results = []

    print("==================================================================")
    print("        DYNAMIC EPSS & CVSS RISK POLICY CALIBRATOR                ")
    print("==================================================================")

    for sig in signatures:
        title = sig.get("name") or sig.get("title") or "Unnamed Signature"
        cvss = float(sig.get("cvss_v4_score") or sig.get("cvss_v4") or 5.0)
        epss = float(sig.get("epss_percentile", 0.1))
        
        # Composite score formula: 40% CVSS impact + 60% empirical EPSS exploitation probability
        composite_score = round((cvss * 0.4) + (epss * 10.0 * 0.6), 2)

        if composite_score >= 8.5:
            policy = "ENFORCE_ACTIVE_DROP"
            log_level = "CRITICAL"
        elif composite_score >= 6.5:
            policy = "ENFORCE_CHALLENGE"
            log_level = "HIGH"
        else:
            policy = "AUDIT_TELEMETRY_ONLY"
            log_level = "MEDIUM"

        calibrated_results.append({
            "id": sig["id"],
            "title": title,
            "cvss_v4": cvss,
            "epss": epss,
            "composite_score": composite_score,
            "recommended_policy": policy,
            "log_level": log_level
        })

        print(f"--> [{sig['id']}] Score: {composite_score}/10 | Policy: {policy} | CVSS: {cvss} | EPSS: {epss}")

    print("==================================================================")
    print(f" Successfully Calibrated {len(calibrated_results)} Threat Signatures.")
    print("==================================================================")
    return calibrated_results

if __name__ == "__main__":
    calibrate_threat_matrix()
