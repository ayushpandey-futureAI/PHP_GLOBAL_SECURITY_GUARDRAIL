#!/usr/bin/env python3
"""
Unit Test Suite: Linux Kernel eBPF / XDP Simulation Runner
==========================================================
Verifies that the simulated eBPF XDP filter accurately drops CGI parameter
injection, soft hyphen bypasses, and stream wrappers at packet ingress.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ebpf.loader import simulate_packet_inspection

def test_ebpf_drops():
    # 1. CGI Argument Injection (CVE-2024-4577)
    pkt1 = b"GET /index.php?-d+allow_url_include=1 HTTP/1.1\r\nHost: target\r\n\r\n"
    assert simulate_packet_inspection(pkt1) == "XDP_DROP", "Failed to drop CGI argument injection"

    # 2. Windows Soft Hyphen Bypass (%ad-d)
    pkt2 = b"GET /index.php?%ad-d+allow_url_include=1 HTTP/1.1\r\nHost: target\r\n\r\n"
    assert simulate_packet_inspection(pkt2) == "XDP_DROP", "Failed to drop soft-hyphen CGI bypass"

    # 3. Path Traversal in URL
    pkt3 = b"GET /../../etc/passwd HTTP/1.1\r\nHost: target\r\n\r\n"
    assert simulate_packet_inspection(pkt3) == "XDP_DROP", "Failed to drop path traversal"

    # 4. Stream Wrapper
    pkt4 = b"POST /index.php HTTP/1.1\r\nHost: target\r\n\r\nphp://input"
    assert simulate_packet_inspection(pkt4) == "XDP_DROP", "Failed to drop stream wrapper"

    print("[PASS] All exploit packets dropped at XDP simulation boundary.")

def test_ebpf_allows_benign():
    # 1. Standard API GET
    pkt1 = b"GET /api/v1/products?category=electronics HTTP/1.1\r\nHost: store.com\r\n\r\n"
    assert simulate_packet_inspection(pkt1) == "XDP_PASS", "Erroneously dropped benign API GET"

    # 2. WordPress Blog Post Request
    pkt2 = b"GET /2026/10/introducing-our-new-platform/ HTTP/1.1\r\nHost: blog.com\r\n\r\n"
    assert simulate_packet_inspection(pkt2) == "XDP_PASS", "Erroneously dropped benign WordPress URL"

    # 3. Form POST
    pkt3 = b"POST /checkout/submit HTTP/1.1\r\nHost: store.com\r\n\r\nname=John&city=NewYork"
    assert simulate_packet_inspection(pkt3) == "XDP_PASS", "Erroneously dropped benign Form POST"

    print("[PASS] All benign packets passed smoothly through XDP simulation.")

if __name__ == "__main__":
    print("==================================================================")
    print("         LINUX eBPF / XDP PACKET INSPECTION TEST RUNNER           ")
    print("==================================================================")
    test_ebpf_drops()
    test_ebpf_allows_benign()
    print("==================================================================")
    print(" [SUCCESS] eBPF / XDP Simulation passed all tests! (100%)         ")
    print("==================================================================")
