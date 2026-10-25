#!/usr/bin/env python3
"""
eBPF / XDP Kernel Program Loader & User-Space Orchestrator
==========================================================
Manages compilation, interface attachment, and telemetry streaming for
the Linux Kernel XDP pre-filter (vaccine_xdp.c).
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

EBPF_SRC = Path(__file__).parent / "vaccine_xdp.c"

def check_kernel_capabilities():
    """Verify if the host operating system supports XDP / eBPF."""
    uname = os.uname()
    kernel_version = uname.release
    print(f"[*] Inspecting Host Kernel: {kernel_version} ({uname.sysname})")
    
    # Check for eBPF filesystem
    bpf_fs = Path("/sys/fs/bpf")
    has_bpf_fs = bpf_fs.exists()
    
    # Check for clang / llvm for compilation
    clang_installed = subprocess.run(["which", "clang"], capture_output=True).returncode == 0
    
    print(f"  -> /sys/fs/bpf mounted: {has_bpf_fs}")
    print(f"  -> Clang toolchain available: {clang_installed}")
    
    return {
        "kernel": kernel_version,
        "bpf_fs": has_bpf_fs,
        "clang": clang_installed,
        "ready": clang_installed and has_bpf_fs
    }

def simulate_packet_inspection(payload_bytes: bytes) -> str:
    """
    Python user-space simulation replicating vaccine_xdp.c logic exactly.
    Used for unit testing and platforms without native root eBPF access.
    """
    # Look for HTTP methods
    if not (payload_bytes.startswith(b"GET") or payload_bytes.startswith(b"POST") or payload_bytes.startswith(b"HEAD")):
        return "XDP_PASS"

    scan_window = payload_bytes[:128]
    scan_lower = scan_window.lower()

    if b"-d allow_" in scan_lower or b"-d+allow_" in scan_lower or b"-d=allow_" in scan_lower:
        return "XDP_DROP"

    # Soft hyphen CGI bypass
    if b"%ad-d" in scan_lower or b"%ad+d" in scan_lower or b"%ad d" in scan_lower:
        return "XDP_DROP"

    if b"../../" in scan_window:
        return "XDP_DROP"

    if b"php://inp" in scan_window:
        return "XDP_DROP"

    return "XDP_PASS"

def compile_xdp_program(target_obj="/tmp/vaccine_xdp.o"):
    """Compile vaccine_xdp.c into eBPF ELF object file."""
    cmd = [
        "clang",
        "-O2",
        "-target", "bpf",
        "-c", str(EBPF_SRC),
        "-o", target_obj
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"[+] eBPF bytecode compiled successfully: {target_obj}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[-] Compilation deferred: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="PHP Vaccine eBPF / XDP Manager")
    parser.add_argument("--check", action="store_true", help="Audit kernel readiness for eBPF")
    parser.add_argument("--compile", action="store_true", help="Compile XDP C program to bytecode")
    parser.add_argument("--simulate", action="store_true", help="Run payload inspection simulation")
    args = parser.parse_args()

    if args.check:
        check_kernel_capabilities()
    elif args.compile:
        compile_xdp_program()
    elif args.simulate:
        test_payload = b"GET /index.php?-d+allow_url_include=1 HTTP/1.1\r\nHost: target\r\n\r\n"
        decision = simulate_packet_inspection(test_payload)
        print(f"Simulated Decision: {decision}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
