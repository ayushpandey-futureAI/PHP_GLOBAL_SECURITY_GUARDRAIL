#!/usr/bin/env python3
"""
Python Test Harness for PHP Vaccine Regex Logic & Payload Interception
Verifies that all regexes in vaccine.php match exploit vectors and permit benign inputs.
"""
import re
import urllib.parse

# 1. CGI Argument Injection Regex
CGI_REGEX = re.compile(r'(-d\s*(?:allow_url_include|auto_prepend_file|auto_append_file|disable_functions|open_basedir|cgi\.fix_pathinfo))', re.I)

# 2. Deserialization / PHP Object Injection Regex
OBJ_REGEX = re.compile(r'(?:^|;|{|})([OaC]):\d+:"[^"]+":\d+:', re.I)

# 3. Stream Wrappers Regex
STREAM_REGEX = re.compile(r'(?:php|data|expect|zip|phar|glob)://', re.I)

# 4. Traversal Regex
TRAVERSAL_REGEX = re.compile(r'\.\.[/\\]')

# 5. Command Injection Regex
CMD_REGEX = re.compile(r'(?:;|\||`|\$\()\s*(?:cat\s+/etc/passwd|whoami|curl\s+[0-9a-z]|wget\s+[0-9a-z]|bash\s+-i|nc\s+-e|python\s+-c)\b', re.I)

# 6. SQLi Regex
SQLI_REGEX = re.compile(r'(?:\bUNION(?:\s+ALL)?\s+SELECT\b|\bSELECT\b.+\bFROM\b.+\bWHERE\b.+\b(?:SLEEP|BENCHMARK)\b|\b1=1\s*--|\bOR\s+[\'"]?1[\'"]?\s*=\s*[\'"]?1\b)', re.I)

def inspect_payload(val):
    decoded = urllib.parse.unquote(str(val))
    if OBJ_REGEX.search(decoded):
        return True, "OBJECT_INJECTION"
    if STREAM_REGEX.search(decoded):
        return True, "STREAM_WRAPPER"
    if "\0" in decoded or TRAVERSAL_REGEX.search(decoded):
        return True, "TRAVERSAL"
    if CMD_REGEX.search(decoded):
        return True, "COMMAND_INJECTION"
    if SQLI_REGEX.search(decoded):
        return True, "SQL_INJECTION"
    return False, "CLEAN"

test_cases = [
    # Malicious
    ("-d allow_url_include=1", "CGI", True),
    ("-d auto_prepend_file=/etc/passwd", "CGI", True),
    ('O:8:"stdClass":1:{s:4:"test";s:4:"hack";}', "OBJ", True),
    ("php://input", "STREAM", True),
    ("data://text/plain;base64,PD9waHA...", "STREAM", True),
    ("../../../../etc/passwd", "TRAVERSAL", True),
    ("127.0.0.1; cat /etc/passwd", "CMD", True),
    ("test || whoami", "CMD", True),
    ("-1 UNION SELECT 1, 2, version() --", "SQLI", True),
    ("SELECT * FROM users WHERE id=1 AND SLEEP(5)", "SQLI", True),
    # Benign
    ("best high performance php frameworks 2026", "CLEAN", False),
    ('{"user_id": 42, "role": "engineer", "status": "active"}', "CLEAN", False),
    ("Hello team, I would like to inquire about the enterprise pricing.", "CLEAN", False),
    ("product-category-electronics_and_appliances", "CLEAN", False)
]

def run_tests():
    print("==================================================================")
    print("    RUNNING PYTHON VACCINE LOGIC VALIDATOR & REGEX VERIFIER      ")
    print("==================================================================")
    passed = 0
    for payload, expected_category, should_block in test_cases:
        if expected_category == "CGI":
            blocked = bool(CGI_REGEX.search(urllib.parse.unquote(payload)))
            cat = "CGI" if blocked else "CLEAN"
        else:
            blocked, cat = inspect_payload(payload)
            
        is_ok = (blocked == should_block)
        status = "PASS" if is_ok else "FAIL"
        if is_ok:
            passed += 1
        print(f"[{status}] Payload: {payload[:40]:<40} -> Blocked: {blocked} ({cat})")
        
    print("==================================================================")
    print(f"Result: {passed}/{len(test_cases)} Tests Passed")
    print("==================================================================")
    assert passed == len(test_cases), "Some tests failed!"

if __name__ == "__main__":
    run_tests()
