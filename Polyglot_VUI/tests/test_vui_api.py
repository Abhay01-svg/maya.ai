#!/usr/bin/env python3
"""Simple test harness: send 5 diverse questions to the Python brain (/process)
and perform basic verification of the responses.
"""
import json
import sys
import subprocess
import os
from time import sleep

import requests


QUESTIONS = [
    ("math", "What is 13 multiplied by 7?"),
    ("geography", "What is the capital of Japan?"),
    ("history", "Who was the first person to walk on the Moon?"),
    ("science", "What causes rainbows to form in the sky?"),
    ("programming", "How do you reverse a string in Python?")
]


def send_question(text):
    url = "http://127.0.0.1:5001/process"
    attempts = 2
    timeout = 20
    for attempt in range(attempts):
        try:
            r = requests.post(url, json={"text": text}, timeout=timeout)
            try:
                return r.json()
            except ValueError:
                return {"error": f"Non-JSON response ({r.status_code}): {r.text[:200]}"}
        except requests.exceptions.RequestException as e:
            last_err = e
            # small backoff before retrying
            sleep(0.5 + attempt * 0.5)
    return {"error": str(last_err)}


def check_health(timeout=1.0):
    url = "http://127.0.0.1:5001/health"
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


def ensure_brain_running(auto_start=True, wait_seconds=6):
    if check_health():
        return True, None

    if not auto_start:
        return False, "brain not running"

    # Attempt to start the Python brain in background
    brain_script = os.path.join("Polyglot_VUI", "python_brain", "app.py")
    log_path = os.path.join("Polyglot_VUI", "tests", "brain_start.log")
    with open(log_path, "a", encoding="utf-8") as lf:
        try:
            popen = subprocess.Popen([sys.executable, brain_script], stdout=lf, stderr=lf, cwd=os.getcwd())
        except Exception as e:
            return False, f"failed to start brain: {e}"

    # wait and poll health
    waited = 0
    interval = 0.5
    while waited < wait_seconds:
        if check_health(timeout=1.0):
            return True, None
        sleep(interval)
        waited += interval

    return False, "brain did not become healthy after start"


def verify_reply(resp):
    if resp is None:
        return False, "no response"
    if "error" in resp:
        return False, resp.get("error")
    reply = resp.get("reply", "").strip()
    if not reply:
        return False, "empty reply"
    # Basic heuristic checks
    if len(reply) < 10:
        return False, f"reply too short: {reply!r}"
    if "error" in reply.lower() or "problem" in reply.lower():
        return False, f"reply indicates an error: {reply!r}"
    return True, reply


def main():
    print("Testing VUI / Python brain endpoint: http://127.0.0.1:5001/process")
    ok, err = ensure_brain_running(auto_start=True, wait_seconds=8)
    if not ok:
        print(f"ERROR: Python brain unavailable: {err}")
        sys.exit(3)
    results = []
    for domain, q in QUESTIONS:
        print(f"\n-> [{domain}] Question: {q}")
        resp = send_question(q)
        ok, detail = verify_reply(resp)
        if ok:
            print(f"   ✅ OK — reply: {detail}")
        else:
            print(f"   ❌ FAIL — reason: {detail}")
        results.append((domain, q, resp, ok, detail))
        sleep(0.5)

    passed = sum(1 for r in results if r[3])
    total = len(results)
    print(f"\nSummary: {passed}/{total} passed")

    # Exit code 0 if all passed, else 2
    sys.exit(0 if passed == total else 2)


if __name__ == "__main__":
    main()
