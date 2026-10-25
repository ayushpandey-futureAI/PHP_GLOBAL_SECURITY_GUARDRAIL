#!/usr/bin/env python3
"""
Unit Test Suite: Online Patching, Scanner & Server Scripts Verification
=======================================================================
Validates the online scanner, auto-patcher script syntax, and console launcher.
"""

import sys
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.online_scanner import PROBES

def test_scanner_probe_definitions():
    assert len(PROBES) >= 5, "Expected at least 5 standard exploit probes!"
    cve_probe = next((p for p in PROBES if "CVE-2024-4577" in p["name"]), None)
    assert cve_probe is not None, "Missing CGI Injection probe!"
    assert cve_probe["expected_code"] == 403, "Expected 403 status code for CGI injection probe"
    print("[PASS] Online Scanner probe definitions verified.")

def test_script_syntax():
    root = Path(__file__).parent.parent
    scripts_to_check = [
        root / "scripts" / "auto_patcher.sh",
        root / "scripts" / "serve_console.sh",
        root / "scripts" / "inoculate.sh"
    ]
    for s in scripts_to_check:
        assert s.exists(), f"Script {s} not found!"
        # Bash syntax check with bash -n
        res = subprocess.run(["bash", "-n", str(s)], capture_output=True, text=True)
        assert res.returncode == 0, f"Syntax error in {s}: {res.stderr}"
        print(f"[PASS] Bash syntax verified for: {s.name}")

if __name__ == "__main__":
    print("==================================================================")
    print("      ONLINE PATCHING & SCANNER TOOLS VERIFICATION TEST           ")
    print("==================================================================")
    test_scanner_probe_definitions()
    test_script_syntax()
    print("==================================================================")
    print(" [SUCCESS] All Online Tooling Tests Passed Successfully! (100%)   ")
    print("==================================================================")
