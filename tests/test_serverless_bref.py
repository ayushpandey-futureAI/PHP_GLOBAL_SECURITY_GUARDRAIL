#!/usr/bin/env python3
"""
Unit Test Suite: AWS Lambda & Bref Serverless Interceptor Test
=============================================================
Validates event structure inspection for API Gateway v1/v2 and ALB.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_exploit_vectors import inspect

def inspect_lambda_event(event: dict) -> tuple[bool, str]:
    # 1. Query String
    if "queryStringParameters" in event and isinstance(event["queryStringParameters"], dict):
        for k, v in event["queryStringParameters"].items():
            blocked, cat = inspect(str(v))
            if blocked: return True, cat

    # 2. Raw Query String
    if "rawQueryString" in event and isinstance(event["rawQueryString"], str):
        blocked, cat = inspect(event["rawQueryString"])
        if blocked: return True, cat

    # 3. Body
    if "body" in event and isinstance(event["body"], str):
        body_str = event["body"]
        blocked, cat = inspect(body_str)
        if blocked: return True, cat

        try:
            json_body = json.loads(body_str)
            if isinstance(json_body, dict):
                for k, v in json_body.items():
                    b, c = inspect(str(v))
                    if b: return True, c
        except Exception:
            pass

    return False, "CLEAN"

def test_lambda_event_interception():
    # 1. Malicious API Gateway v1 query string
    event1 = {
        "httpMethod": "GET",
        "path": "/users",
        "queryStringParameters": {
            "sort": "-d allow_url_include=1"
        }
    }
    blocked, cat = inspect_lambda_event(event1)
    assert blocked and cat == "CGI_ARG_INJECTION", "Failed to block CGI injection in Lambda query"

    # 2. Malicious API Gateway v2 rawQueryString
    event2 = {
        "rawQueryString": "%ad-d+allow_url_include=1",
        "requestContext": {"http": {"method": "GET"}}
    }
    blocked, cat = inspect_lambda_event(event2)
    assert blocked and cat == "CGI_ARG_INJECTION", "Failed to block soft hyphen in API Gateway v2"

    # 3. Malicious JSON Body with Deserialization
    event3 = {
        "httpMethod": "POST",
        "body": json.dumps({"payload": 'O:8:"stdClass":1:{s:4:"test";s:4:"hack";}'})
    }
    blocked, cat = inspect_lambda_event(event3)
    assert blocked and cat == "OBJECT_INJECTION", "Failed to block deserialization bomb in Lambda body"

    print("[PASS] All malicious serverless Lambda events successfully blocked.")

def test_lambda_event_benign():
    # Standard clean e-commerce event
    event = {
        "httpMethod": "POST",
        "path": "/cart/checkout",
        "queryStringParameters": {"currency": "USD"},
        "body": json.dumps({
            "item_id": 4920,
            "quantity": 2,
            "delivery_note": "Please leave at front door near mailbox"
        })
    }
    blocked, cat = inspect_lambda_event(event)
    assert not blocked, "Erroneously blocked clean serverless event"
    print("[PASS] Clean serverless Lambda event passed without disruption.")

if __name__ == "__main__":
    print("==================================================================")
    print("         AWS LAMBDA & BREF SERVERLESS INTERCEPTOR TEST            ")
    print("==================================================================")
    test_lambda_event_interception()
    test_lambda_event_benign()
    print("==================================================================")
    print(" [SUCCESS] Serverless Bref Interceptor passed all checks! (100%)  ")
    print("==================================================================")
