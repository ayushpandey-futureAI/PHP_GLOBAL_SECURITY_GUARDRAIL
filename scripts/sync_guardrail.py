#!/usr/bin/env python3
"""
PHP Global Security Guardrail - Continuous Synchronizer & Cloud Mirror
======================================================================
Synchronizes code, documentation, sprint logs, and research between:
- Local Workspace: /home/ayush-pandey/PHP_GLOBAL_SECURITY_GUARDRAIL
- Google Drive Remote: gdrive:PHP_Global_Security_Guardrail
- Remote GitHub Repository: ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL

Usage:
  python3 scripts/sync_guardrail.py          # One-time sync & git commit/push
  python3 scripts/sync_guardrail.py --daemon # Continuous 600s background sync
"""

import os
import sys
import time
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

LOCAL_ROOT = Path(__file__).resolve().parent.parent
RCLONE_BIN = Path(os.environ.get("RCLONE_BIN", "/home/ayush-pandey/.local/bin/rclone"))
GDRIVE_REMOTE = os.environ.get("GDRIVE_REMOTE", "gdrive:PHP_Global_Security_Guardrail")

def sync_to_gdrive():
    """Syncs local files to Google Drive using direct rclone binary."""
    now_str = datetime.now(timezone.utc).isoformat()
    print(f"[{now_str}] Syncing files to Google Drive ({GDRIVE_REMOTE})...")
    
    if not RCLONE_BIN.exists():
        print(f"[!] Error: rclone binary not found at {RCLONE_BIN}")
        return False

    cmd = [
        str(RCLONE_BIN),
        "copy",
        str(LOCAL_ROOT),
        GDRIVE_REMOTE,
        "--exclude", ".git/**",
        "--exclude", "__pycache__/**",
        "--exclude", "*.pyc",
        "--update",
        "--transfers", "4",
        "-v"
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("[+] Google Drive sync complete via rclone.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] rclone error: {e.stderr}")
        return False

def sync_to_github(auto_push=True):
    """Commits and pushes changes to GitHub using Git CLI."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now_str}] Checking Git status and pushing to GitHub...")
    
    try:
        if not (LOCAL_ROOT / ".git").exists():
            print("[!] Git not initialized in local root.")
            return False

        subprocess.run(["git", "add", "."], cwd=LOCAL_ROOT, check=True)
        status = subprocess.run(["git", "status", "--porcelain"], cwd=LOCAL_ROOT, capture_output=True, text=True, check=True)
        
        if status.stdout.strip():
            commit_msg = f"feat(guardrail): automated sync & security update [{now_str}]"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=LOCAL_ROOT, check=True)
            print(f"  -> Committed changes: {commit_msg}")
        else:
            print("  -> No git changes to commit.")

        if auto_push:
            push_res = subprocess.run(["git", "push", "origin", "main"], cwd=LOCAL_ROOT, capture_output=True, text=True)
            if push_res.returncode == 0:
                print("  -> Successfully pushed to GitHub origin/main.")
            else:
                print(f"  -> Git push notice: {push_res.stderr.strip()}")
                
        return True
    except Exception as e:
        print(f"[ERROR] Git sync error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="PHP Guardrail Sync Engine")
    parser.add_argument("--daemon", action="store_true", help="Run continuously in background (600s loop)")
    parser.add_argument("--interval", type=int, default=600, help="Interval in seconds for daemon mode")
    args = parser.parse_args()

    if args.daemon:
        print(f"[+] Starting Continuous Sync Daemon (Interval: {args.interval}s)...")
        while True:
            try:
                sync_to_gdrive()
                sync_to_github()
            except Exception as e:
                print(f"[!] Daemon error during sync: {e}")
            time.sleep(args.interval)
    else:
        sync_to_gdrive()
        sync_to_github()

if __name__ == "__main__":
    main()
