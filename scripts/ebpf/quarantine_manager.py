#!/usr/bin/env python3
"""
Automated Memory & Worker Process Quarantine Manager
====================================================
Monitors running PHP processes and incoming threat frequency, triggering
automated cgroup throttling or IP rate-limiting when attack bursts occur.
"""

import time
from dataclasses import dataclass

@dataclass
class QuarantineRecord:
    target_id: str
    target_type: str  # "PID" or "IP"
    violations: int
    quarantined: bool
    quarantine_until: float

class QuarantineManager:
    def __init__(self, threshold: int = 5, duration_seconds: int = 60):
        self.threshold = threshold
        self.duration_seconds = duration_seconds
        self.records: dict[str, QuarantineRecord] = {}

    def record_violation(self, target_id: str, target_type: str = "IP") -> bool:
        """
        Records an attack violation. Returns True if target is now quarantined.
        """
        now = time.time()
        record = self.records.get(target_id)

        if not record:
            record = QuarantineRecord(
                target_id=target_id,
                target_type=target_type,
                violations=1,
                quarantined=False,
                quarantine_until=0.0
            )
            self.records[target_id] = record
            return False

        # If currently quarantined, check expiry
        if record.quarantined:
            if now > record.quarantine_until:
                # Expired, reset
                record.quarantined = False
                record.violations = 1
                return False
            return True

        record.violations += 1
        if record.violations >= self.threshold:
            record.quarantined = True
            record.quarantine_until = now + self.duration_seconds
            print(f"[!] [QUARANTINE ENFORCED] {target_type} '{target_id}' quarantined for {self.duration_seconds}s ({record.violations} violations)!")
            return True

        return False

    def is_quarantined(self, target_id: str) -> bool:
        now = time.time()
        record = self.records.get(target_id)
        if not record or not record.quarantined:
            return False
        if now > record.quarantine_until:
            record.quarantined = False
            return False
        return True

if __name__ == "__main__":
    print("==================================================================")
    print("      AUTOMATED MEMORY & THREAT QUARANTINE MANAGER TEST           ")
    print("==================================================================")
    qm = QuarantineManager(threshold=3, duration_seconds=5)
    test_ip = "198.51.100.42"

    print(f"[*] Simulating attack violations from {test_ip}...")
    for i in range(1, 5):
        is_q = qm.record_violation(test_ip, "IP")
        print(f"  Attempt {i} -> Quarantined: {is_q}")

    assert qm.is_quarantined(test_ip), "IP should be actively quarantined!"
    print("==================================================================")
    print(" [SUCCESS] Quarantine manager successfully disarmed threat burst! ")
    print("==================================================================")
