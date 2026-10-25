#!/usr/bin/env python3
"""
Unit Test Suite: Sprint 7 Threat Mesh, Quarantine & Open-Source Packaging
=========================================================================
Validates composer.json, WordPress plugin zip, P2P mesh, and quarantine logic.
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.mesh.p2p_gossip_mesh import ThreatGossipNode
from scripts.ebpf.quarantine_manager import QuarantineManager
from scripts.simulate_pilot_deployment import run_pilot_simulation

ROOT = Path(__file__).parent.parent

def test_composer_json_validity():
    composer_file = ROOT / "composer.json"
    assert composer_file.exists(), "composer.json missing!"
    data = json.loads(composer_file.read_text(encoding="utf-8"))
    assert data["name"] == "ayushpandey-futureai/php-universal-vaccine"
    assert "src/vaccine.php" in data["autoload"]["files"]
    print("[PASS] composer.json package definition verified.")

def test_wordpress_distributable_exists():
    zip_file = ROOT / "dist" / "php-vaccine-guardrail-v1.3.0.zip"
    assert zip_file.exists(), "WordPress plugin zip file missing!"
    assert zip_file.stat().st_size > 1000, "Plugin zip file too small!"
    print(f"[PASS] WordPress plugin zip verified ({zip_file.stat().st_size:,} bytes).")

def test_p2p_gossip_mesh_logic():
    node1 = ThreatGossipNode("node-01", "test-secret-key-1234")
    node2 = ThreatGossipNode("node-02", "test-secret-key-1234")

    envelope = node1.generate_threat_envelope(
        threat_id="THREAT-TEST-001",
        category="SQL_INJECTION",
        pattern=r"UNION\s+SELECT",
        severity="HIGH"
    )

    # Valid signature absorption
    assert node2.verify_and_absorb_envelope(envelope) == True, "Peer failed to absorb valid threat packet!"
    assert "THREAT-TEST-001" in node2.signatures_catalog, "Threat not cataloged by peer!"

    # Tampered signature absorption rejection
    tampered = dict(envelope)
    tampered["signature"] = "badc0de" + tampered["signature"][7:]
    assert node2.verify_and_absorb_envelope(tampered) == False, "Tampered packet was erroneously accepted!"

    print("[PASS] P2P threat gossip cryptographic verification and rejection verified.")

def test_quarantine_manager_logic():
    qm = QuarantineManager(threshold=3, duration_seconds=10)
    target = "10.0.0.99"
    assert qm.record_violation(target) == False
    assert qm.record_violation(target) == False
    assert qm.record_violation(target) == True  # 3rd violation triggers quarantine
    assert qm.is_quarantined(target) == True
    print("[PASS] Quarantine threshold and enforcement verified.")

def test_pilot_deployment_run():
    assert run_pilot_simulation() == True, "Pilot deployment simulation failed!"
    print("[PASS] Synthetic pilot deployment passed.")

if __name__ == "__main__":
    print("==================================================================")
    print("   SPRINT 7 THREAT MESH, QUARANTINE & PACKAGING VERIFICATION     ")
    print("==================================================================")
    test_composer_json_validity()
    test_wordpress_distributable_exists()
    test_p2p_gossip_mesh_logic()
    test_quarantine_manager_logic()
    test_pilot_deployment_run()
    print("==================================================================")
    print(" [SUCCESS] All Sprint 7 & Packaging Tests Passed! (100%)          ")
    print("==================================================================")
