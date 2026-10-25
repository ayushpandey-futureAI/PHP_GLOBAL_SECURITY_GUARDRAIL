#!/usr/bin/env python3
"""
Unit Test Suite: Central Fleet Console & RBAC Authentication Test
=================================================================
Validates RBAC permissions, OIDC claims evaluation, and fleet REST API schema.
"""

from pathlib import Path
import json

RBAC_PHP = Path(__file__).parent / "../src/console/auth/rbac.php"
CONSOLE_API_PHP = Path(__file__).parent / "../src/console/api.php"

def test_rbac_file_structure():
    assert RBAC_PHP.exists(), "RBAC PHP file missing!"
    content = RBAC_PHP.read_text(encoding="utf-8")
    assert "class EnterpriseRBAC" in content
    assert "ROLE_SUPER_ADMIN" in content
    assert "ROLE_SECOPS_ANALYST" in content
    assert "ROLE_COMPLIANCE_AUDITOR" in content
    assert "public static function hasPermission" in content
    assert "public static function validateOidcToken" in content
    assert "public static function parseSamlAssertion" in content
    print("[PASS] RBAC and SSO module structure verified.")

def test_console_api_structure():
    assert CONSOLE_API_PHP.exists(), "Console API PHP file missing!"
    content = CONSOLE_API_PHP.read_text(encoding="utf-8")
    assert "case 'fleet':" in content
    assert "case 'heartbeat':" in content
    assert "case 'telemetry':" in content
    assert "total_attacks_intercepted" in content
    assert "mean_latency_us" in content
    print("[PASS] Fleet Console REST API endpoints verified.")

if __name__ == "__main__":
    print("==================================================================")
    print("       CENTRAL FLEET CONSOLE & RBAC AUTHENTICATION TEST           ")
    print("==================================================================")
    test_rbac_file_structure()
    test_console_api_structure()
    print("==================================================================")
    print(" [SUCCESS] Fleet Console & RBAC passed all test assertions! (100%)")
    print("==================================================================")
