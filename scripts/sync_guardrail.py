#!/usr/bin/env python3
"""
PHP Global Security Guardrail - Continuous Synchronizer & Cloud Mirror
======================================================================
Synchronizes code, documentation, sprint logs, and research between:
- Local Workspace: /home/ayush-pandey/PHP_GLOBAL_SECURITY_GUARDRAIL
- Google Drive Cloud Mirror: /home/ayush-pandey/GoogleDrive/PHP_Global_Security_Guardrail
- Remote GitHub Repository: ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL

Usage:
  python3 scripts/sync_guardrail.py          # One-time sync & git commit/push
  python3 scripts/sync_guardrail.py --daemon # Continuous 600s background sync
"""

import os
import sys
import time
import shutil
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

LOCAL_ROOT = Path("/home/ayush-pandey/PHP_GLOBAL_SECURITY_GUARDRAIL")
GDRIVE_ROOT = Path("/home/ayush-pandey/GoogleDrive/PHP_Global_Security_Guardrail")
LOGS_DIR = LOCAL_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

SYNC_FILES = [
    "AGENT.md",
    "JIRA_SPRINTS.md",
    "PROJECT_MEMORY.md",
    "CONVERSATION_LOGS.md",
    "README.md",
    ".gitignore"
]

SYNC_DIRS = [
    "src",
    "scripts",
    "tests",
    "docs"
]

def sync_to_gdrive():
    """Syncs local files to the Google Drive mount."""
    now_str = datetime.now(timezone.utc).isoformat()
    print(f"[{now_str}] Syncing files to Google Drive ({GDRIVE_ROOT})...")
    
    if not GDRIVE_ROOT.exists():
        print(f"[!] Warning: Google Drive path {GDRIVE_ROOT} does not exist or is not mounted.")
        return False

    # Sync individual files
    for fname in SYNC_FILES:
        src = LOCAL_ROOT / fname
        dst = GDRIVE_ROOT / fname
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  -> Synced file: {fname}")

    # Sync directories
    for dname in SYNC_DIRS:
        src_dir = LOCAL_ROOT / dname
        dst_dir = GDRIVE_ROOT / dname
        if src_dir.exists():
            if dst_dir.exists():
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            print(f"  -> Synced directory: {dname}/")

    print("[+] Google Drive sync complete.")
    return True

def sync_to_github(auto_push=True):
    """Commits and pushes changes to GitHub using Git CLI."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now_str}] Checking Git status and pushing to GitHub...")
    
    try:
        # Check if git is initialized
        if not (LOCAL_ROOT / ".git").exists():
            print("[!] Git not initialized in local root.")
            return False

        # Add all files
        subprocess.run(["git", "add", "."], cwd=LOCAL_ROOT, check=True)
        
        # Check if there are changes to commit
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
                print(f"  -> Git push warning/notice: {push_res.stderr.strip()}")
                
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
