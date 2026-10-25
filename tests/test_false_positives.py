#!/usr/bin/env python3
"""
FALSE POSITIVE RIGOROUS TEST HARNESS: PHP UNIVERSAL VACCINE
Validates that legitimate web traffic, complex CMS interactions (WordPress, WooCommerce, Drupal),
JSON API bodies, and natural language texts are 100% permitted without interference.
"""

import sys
from test_exploit_vectors import inspect

BENIGN_PAYLOADS = [
    # 1. Natural Language with SQL / Command Keywords
    ("Please select the department you wish to contact from the drop-down menu.", "Form Label"),
    ("The union of European postal workers called for higher baseline wages.", "News Article"),
    ("I need 8 hours of sleep every night to stay productive.", "Forum Comment"),
    ("The benchmark for our Q3 performance was exceeded by 15 percent.", "Annual Review"),
    ("Order #90214 has been placed successfully by customer.", "E-Commerce Notice"),
    ("Where did you put the documentation files for the project?", "Support Ticket"),

    # 2. WordPress Gutenberg & REST API JSON Bodies
    ('{"id": 412, "title": {"rendered": "Getting Started with Modern Web Development"}, "content": "<!-- wp:paragraph --><p>Welcome to our new site!</p><!-- /wp:paragraph -->"}', "Gutenberg Block"),
    ('{"status": "publish", "categories": [12, 18], "tags": ["php", "security", "linux"]}', "WP REST Post"),

    # 3. Base64 Data URIs for Inline Images (RFC 2397)
    ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==", "Inline PNG Data URI"),
    ("data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=", "Inline JPEG Data URI"),

    # 4. Standard URLs and Query Strings
    ("https://example.com/store/catalog?sort=price_asc&filter=electronics&page=2", "Catalog URL"),
    ("https://api.github.com/repos/ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL", "GitHub API URL"),
    ("redirect_to=https%3A%2F%2Fdashboard.domain.com%2Foverview%3Fuser%3D45", "Encoded Redirect URL"),

    # 5. Punctuation, Semicolons & Pipe Usage
    ("He arrived early; therefore, he had to wait for the doors to open.", "Sentence with Semicolon"),
    ("Command line piping (like cmd1 | cmd2) is an essential Unix paradigm.", "Technical Tutorial"),
    ("Status: Ready | Mode: Production | Region: ap-south-1", "Status Bar String"),

    # 6. E-Commerce Checkout & Address Fields
    ("Flat 402, Block B, Royal Heritage Apartments, MG Road, Bengaluru, 560001", "Delivery Address"),
    ("Special instructions: Please ring the doorbell twice and leave package at door.", "Delivery Instructions"),

    # 7. Code Snippets in Developer Portals
    ("function calculate_tax($price, $rate) { return $price * $rate; }", "PHP Code Snippet"),
    ("SELECT_ALL_ITEMS_FLAG = True", "Constant Definition"),
    ("const API_TIMEOUT_MS = 5000;", "JavaScript Constant")
]

def run():
    print("==================================================================")
    print("   PHP UNIVERSAL VACCINE: BENIGN TRAFFIC & FALSE POSITIVE TEST   ")
    print("==================================================================")
    passed = 0
    false_positives = []

    for payload, description in BENIGN_PAYLOADS:
        blocked, detected_cat = inspect(payload)
        if not blocked:
            passed += 1
            print(f" [PASS] Allowed (200 OK) -> {description:<30} Payload: {payload[:40]}")
        else:
            false_positives.append((payload, description, detected_cat))
            print(f" [FAIL] FALSE POSITIVE! Flagged as [{detected_cat}] on: {payload}")

    print("==================================================================")
    print(f" Benign Traffic Pass Rate: {passed}/{len(BENIGN_PAYLOADS)} ({passed/len(BENIGN_PAYLOADS)*100:.1f}%)")
    print("==================================================================")

    if false_positives:
        print("[!] False positives detected! Refinement required:")
        for p, d, cat in false_positives:
            print(f"    - Flagged as {cat}: {p}")
        sys.exit(1)
    else:
        print("[SUCCESS] Zero false positives! Legitimate web traffic passes flawlessly.")

if __name__ == "__main__":
    run()
