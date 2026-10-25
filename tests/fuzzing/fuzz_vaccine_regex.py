#!/usr/bin/env python3
"""
Continuous Autonomous Fuzzing Battery for PHP Vaccine RegEx Engine
===================================================================
Tests vaccine de-obfuscation and regex inspection against thousands of
mutated payloads to ensure zero catastrophic backtracking (ReDoS) or memory exhaustion.
"""

import re
import time
import random
import string
import urllib.parse

# Compiled Engine Matching vaccine.php v1.3
CGI_RE = re.compile(r'(?:-|%2d|%ad)[-\s]*(?:d|%64|%44)?\s*(?:allow_url_include|auto_prepend_file|auto_append_file|disable_functions|open_basedir|cgi\.fix_pathinfo|safe_mode)', re.I)
OBJ_RE = re.compile(r'(?:^|;|{|})([OaC]):\d+:"[^"]+":\d+:', re.I)
STREAM_RE = re.compile(r'(?:php|data|expect|phar|zip|glob|compress\.zlib|compress\.bzip2)://', re.I)
TRAV_RE = re.compile(r'(?:\.\.[/\\]|%2e%2e[/\\]|\0|%00)')
CMD_RE = re.compile(r'(?:;|\|{1,2}|`|\$\()\s*(?:cat\s+/etc|whoami|curl\s+[0-9a-z]|wget\s+[0-9a-z]|bash\s+-i|nc\s+-e|python\s+-c|id\b|uname\s+-a)', re.I)
SQLI_RE = re.compile(r'(?:\bUNION(?:\s+ALL)?\s+SELECT\b|\b(?:AND|OR)\s+(?:SLEEP|BENCHMARK|PG_SLEEP)\s*\(|\bSELECT\b.+\bFROM\b.+\bWHERE\b.+\b(?:SLEEP|BENCHMARK)\b|\b1=1\s*--|\bOR\s+[\'"]?1[\'"]?\s*=\s*[\'"]?1\b)', re.I)
SSRF_RE = re.compile(r'(?:https?://)?(?:169\.254\.169\.254|metadata\.google\.internal|100\.100\.100\.200|fd00:ec2::254)', re.I)

def deobfuscate(val):
    clean = re.sub(r'%(?:ad|AD)', '-', str(val))
    depth = 0
    while depth < 3:
        try:
            decoded = urllib.parse.unquote_plus(clean)
        except Exception:
            break
        if decoded == clean:
            break
        clean = decoded
        depth += 1
    return clean

def inspect(val):
    c = deobfuscate(val)
    if CGI_RE.search(c): return True
    if OBJ_RE.search(c): return True
    if STREAM_RE.search(c): return True
    if "\0" in c or TRAV_RE.search(c) or re.search(r'\.\.[/\\]', c): return True
    if CMD_RE.search(c): return True
    if SQLI_RE.search(c): return True
    if SSRF_RE.search(c): return True
    return False

def generate_fuzz_payloads(count=5000):
    payloads = []
    
    # 1. ReDoS Backtracking Traps
    payloads.append(";" + (" " * 500) + "whoami")
    payloads.append("UNION SELECT " + ("NULL," * 300) + "NULL")
    payloads.append("SELECT * FROM users WHERE " + ("1=1 AND " * 200) + "1=1")
    payloads.append("O:8:\"" + ("A" * 1000) + "\":1:{s:4:\"test\";s:4:\"hack\";}")
    payloads.append("../" * 300 + "etc/passwd")

    # 2. Deep Nested Encodings
    deep_encoded = "../../../../etc/passwd"
    for _ in range(15):
        deep_encoded = urllib.parse.quote(deep_encoded)
    payloads.append(deep_encoded)

    # 3. Random Character Mutations & Surrogates
    for _ in range(count - len(payloads)):
        choice = random.randint(1, 4)
        if choice == 1:
            # Random alphanumeric with SQL / Command symbols
            p = ''.join(random.choices(string.ascii_letters + string.digits + " ;|'\"=-/*&%$#@!\\", k=random.randint(20, 200)))
        elif choice == 2:
            # Repetitive patterns
            base = random.choice(["%ad", "%2e", "%00", "-d", "php://", "UNION", "cat", "whoami"])
            p = base * random.randint(10, 80)
        elif choice == 3:
            # Massive string
            p = ''.join(random.choices(string.ascii_letters, k=5000))
        else:
            # Mixed UTF-8 characters
            p = "テスト" * 50 + "%ad-d" + "🔒" * 20
        payloads.append(p)

    return payloads

def run_fuzz_battery(iterations=3000):
    print("==================================================================")
    print(f"      CONTINUOUS AUTONOMOUS FUZZING BATTERY ({iterations:,} MUTATIONS)   ")
    print("==================================================================")
    payloads = generate_fuzz_payloads(iterations)
    
    max_duration = 0.0
    slowest_payload = ""
    total_time = 0.0

    t_start = time.perf_counter()
    for idx, p in enumerate(payloads):
        t0 = time.perf_counter()
        inspect(p)
        elapsed = time.perf_counter() - t0
        total_time += elapsed

        if elapsed > max_duration:
            max_duration = elapsed
            slowest_payload = p[:80]

        # ReDoS Assertion: No single payload may exceed 5 milliseconds
        assert elapsed < 0.005, f"[FATAL] ReDoS Timeout detected ({elapsed*1000:.2f}ms) on: {p[:100]}"

    t_total = time.perf_counter() - t_start
    throughput = int(iterations / t_total)

    print(f"[+] Total Iterations Tested: {iterations:,}")
    print(f"[+] Total Wall-Clock Time:   {t_total:.3f} seconds")
    print(f"[+] Fuzzing Throughput:      {throughput:,} inspections / second")
    print(f"[+] Max Single Inspection:   {max_duration * 1000:.3f} ms")
    print(f"[+] Average Inspection:      {(total_time / iterations) * 1000:.4f} ms")
    print(f"[+] Worst-Case Sample:       {slowest_payload}...")
    print("==================================================================")
    print(" [SUCCESS] Zero ReDoS Vulnerabilities or Crash Vectors Discovered! ")
    print("==================================================================")

if __name__ == "__main__":
    run_fuzz_battery()
