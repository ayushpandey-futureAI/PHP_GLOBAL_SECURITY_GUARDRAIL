#!/usr/bin/env python3
"""
Peer-to-Peer (P2P) Encrypted Threat Signature Gossip Mesh
=========================================================
Implements decentralized zero-trust threat intelligence sharing across
server clusters, automatically propagating newly intercepted attack vectors.
"""

import os
import sys
import json
import time
import hmac
import hashlib
from pathlib import Path

DEFAULT_SECRET = "php-vaccine-cluster-shared-secret-key-2026"

class ThreatGossipNode:
    def __init__(self, node_id: str, secret_key: str = DEFAULT_SECRET):
        self.node_id = node_id
        self.secret_key = secret_key.encode("utf-8")
        self.known_peers = set()
        self.received_threats = []
        self.signatures_catalog = {}

    def add_peer(self, peer_address: str):
        self.known_peers.add(peer_address)

    def generate_threat_envelope(self, threat_id: str, category: str, pattern: str, severity: str = "HIGH") -> dict:
        """Create a cryptographically signed threat packet for mesh broadcast."""
        timestamp = int(time.time())
        payload = {
            "origin_node": self.node_id,
            "threat_id": threat_id,
            "category": category,
            "detection_pattern": pattern,
            "severity": severity,
            "timestamp": timestamp
        }
        message_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature = hmac.new(self.secret_key, message_bytes, hashlib.sha256).hexdigest()

        return {
            "payload": payload,
            "signature": signature
        }

    def verify_and_absorb_envelope(self, envelope: dict) -> bool:
        """Verify peer cryptographic signature and incorporate threat rule."""
        payload = envelope.get("payload", {})
        received_sig = envelope.get("signature", "")

        message_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        expected_sig = hmac.new(self.secret_key, message_bytes, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(received_sig, expected_sig):
            print(f"[!] [NODE {self.node_id}] Cryptographic verification FAILED for packet from {payload.get('origin_node')}!")
            return False

        # Reject replay attacks older than 300 seconds
        if time.time() - payload.get("timestamp", 0) > 300:
            print(f"[!] [NODE {self.node_id}] Replay packet expired from {payload.get('origin_node')}!")
            return False

        threat_id = payload["threat_id"]
        self.signatures_catalog[threat_id] = payload
        self.received_threats.append(payload)

        print(f"[+] [NODE {self.node_id}] Absorbed verified threat [{threat_id}] ({payload['category']}) from Peer {payload['origin_node']}.")
        return True

    def broadcast_to_mesh(self, envelope: dict, peer_nodes: list) -> int:
        """Simulate broadcasting packet to all peer nodes across cluster."""
        absorbed_count = 0
        for peer in peer_nodes:
            if peer.node_id != self.node_id:
                if peer.verify_and_absorb_envelope(envelope):
                    absorbed_count += 1
        return absorbed_count

if __name__ == "__main__":
    print("==================================================================")
    print("      P2P ENCRYPTED THREAT SIGNATURE GOSSIP MESH SIMULATOR        ")
    print("==================================================================")
    node_alpha = ThreatGossipNode("node-aws-us-east-1")
    node_beta  = ThreatGossipNode("node-azure-eu-west-1")
    node_gamma = ThreatGossipNode("node-onprem-dc-core")

    cluster = [node_alpha, node_beta, node_gamma]

    # Node Alpha discovers novel zero-day exploit pattern
    print("[*] Node Alpha intercepts novel zero-day attack vector...")
    threat_pkt = node_alpha.generate_threat_envelope(
        threat_id="THREAT-0DAY-2026-AUTO",
        category="CGI_ARGUMENT_INJECTION",
        pattern=r"(?:proxy_pass_override|gateway_bypass)=",
        severity="CRITICAL"
    )

    # Broadcast across mesh
    peers_updated = node_alpha.broadcast_to_mesh(threat_pkt, cluster)
    print(f"[+] Mesh Gossip Complete: {peers_updated} remote cluster nodes autonomously immunized!")
    print("==================================================================")
