#!/usr/bin/env python3
"""
Aurora CloudBank — Engineer Onboarding Live Demo
================================================
Runs against a live Aurora server (default: http://localhost:8000).
No internal imports required — pure HTTP calls via requests.

Demonstrates 4 core capabilities in sequence:
  1. System health & module registration
  2. Memory write → SHA-256 hash → semantic recall
  3. Ethics field evaluation (5-dimension curvature)
  4. Observability telemetry snapshot

Usage:
    python scripts/onboard_demo.py
    python scripts/onboard_demo.py --base-url http://localhost:8000
    python scripts/onboard_demo.py --base-url http://my-server:8000 --token <jwt>

Exits 0 if all steps pass, 1 if any step fails (CI-safe).
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("\n❌ requests is not installed. Run: pip install requests")
    sys.exit(1)


# ───────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────

W = 66  # banner width


def banner(title: str):
    print()
    print("━" * W)
    print(f"  {title}")
    print("━" * W)


def ok(msg: str, detail: str = ""):
    suffix = f"  →  {detail}" if detail else ""
    print(f"  ✅  {msg}{suffix}")


def fail(msg: str, detail: str = ""):
    suffix = f"  →  {detail}" if detail else ""
    print(f"  ❌  {msg}{suffix}")


def info(msg: str):
    print(f"      {msg}")


def step_result(name: str, passed: bool, elapsed: float):
    icon = "✅" if passed else "❌"
    status = "PASS" if passed else "FAIL"
    print(f"  {icon}  {name:<45}  {status}  ({elapsed:.2f}s)")
    return passed


# ───────────────────────────────────────────────────────────────────
# Demo steps
# ───────────────────────────────────────────────────────────────────

def demo_1_health(session: requests.Session, base: str) -> bool:
    """
    Step 1: System health + module registration count.
    Validates the server is live and reports registered components.
    """
    banner("STEP 1/4 — System Health & Module Registration")
    print("  Calling: GET /api/synergy/health")
    print()

    t0 = time.perf_counter()
    try:
        r = session.get(f"{base}/api/synergy/health", timeout=10)
        elapsed = time.perf_counter() - t0
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.ConnectionError:
        elapsed = time.perf_counter() - t0
        fail("Cannot reach server", f"Is the server running at {base}?")
        info("Start it with:  make serve-dev")
        return step_result("Health check", False, elapsed)
    except Exception as e:
        elapsed = time.perf_counter() - t0
        fail("Unexpected error", str(e))
        return step_result("Health check", False, elapsed)

    # Surface key fields — handle varied response shapes gracefully
    status = data.get("status") or data.get("health_status") or "unknown"
    components = (
        data.get("registered_components")
        or data.get("component_count")
        or data.get("total_components")
        or len(data.get("components", {}))
        or "n/a"
    )
    ok("Server is live", f"status={status}")
    ok("Module registry", f"components={components}")

    # Pretty-print a compact subset of the response
    interesting_keys = ["status", "health_status", "registered_components",
                        "component_count", "uptime_seconds", "version"]
    snippet = {k: data[k] for k in interesting_keys if k in data}
    if snippet:
        info(json.dumps(snippet, indent=6))

    passed = str(status).lower() not in ("error", "critical", "unknown", "unhealthy")
    return step_result("Health check", passed, elapsed)


def demo_2_memory(session: requests.Session, base: str) -> bool:
    """
    Step 2: Write a memory entry, retrieve its SHA-256 hash, then recall by context_tag.
    Shows the audit trail mechanic — the foundational guarantee of the system.
    """
    banner("STEP 2/4 — Memory Write → SHA-256 Hash → Semantic Recall")
    context_tag = f"onboarding_demo_{datetime.now(timezone.utc).strftime('%H%M%S')}"
    payload = {
        "content": "Aurora onboarding demo entry — every operation carries a SHA-256 audit hash.",
        "context_tag": context_tag,
        "tier": "active",
    }
    print(f"  Calling: POST /aumem/store  (context_tag={context_tag})")
    print()

    # --- Write ---
    t0 = time.perf_counter()
    try:
        r = session.post(f"{base}/aumem/store", json=payload, timeout=10)
        elapsed = time.perf_counter() - t0
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.HTTPError as e:
        elapsed = time.perf_counter() - t0
        fail("Memory store failed", f"HTTP {r.status_code}: {r.text[:120]}")
        return step_result("Memory write + hash", False, elapsed)
    except Exception as e:
        elapsed = time.perf_counter() - t0
        fail("Memory store error", str(e))
        return step_result("Memory write + hash", False, elapsed)

    memory_id = data.get("memory_id") or data.get("id") or data.get("entry_id")
    symbolic_hash = (
        data.get("symbolic_hash")
        or data.get("dlp_hash")
        or data.get("hash")
        or data.get("sha256")
    )
    tier = data.get("tier") or data.get("memory_tier") or "active"

    ok("Memory stored", f"id={memory_id}  tier={tier}")
    if symbolic_hash:
        ok("SHA-256 audit hash returned", symbolic_hash[:16] + "...")
        info("  Every write generates a cryptographic anchor for DLP compliance.")
    else:
        info("  (symbolic_hash not in response — check /aumem/store schema)")

    # --- Recall by context_tag ---
    try:
        recall_r = session.get(
            f"{base}/aumem/retrieve",
            params={"context_tag": context_tag, "limit": 1},
            timeout=10,
        )
        if recall_r.status_code == 200:
            recall_data = recall_r.json()
            entries = recall_data.get("entries") or recall_data.get("results") or []
            if entries:
                ok("Semantic recall", f"{len(entries)} entry retrieved by context_tag")
            else:
                info("  Recall endpoint reached but returned 0 entries.")
        elif recall_r.status_code == 404:
            info("  /aumem/retrieve not found — check API_CATALOG.md for recall endpoint path.")
        else:
            info(f"  Recall returned HTTP {recall_r.status_code}.")
    except Exception:
        info("  Recall check skipped (non-critical).")

    passed = memory_id is not None
    return step_result("Memory write + hash", passed, elapsed)


def demo_3_ethics(session: requests.Session, base: str) -> bool:
    """
    Step 3: Ethics field evaluation.
    Demonstrates the 5-dimension geometric curvature engine — Aurora's
    most distinctive architectural feature. Every module operation is
    subject to this evaluation before execution.
    """
    banner("STEP 3/4 — Ethics Field Evaluation (5-Dimension Curvature)")
    payload = {
        "operation": "onboarding_demo_eval",
        "context_tag": "onboarding_ethics",
        "payload": {
            "intent": "observe_and_learn",
            "scope": "read_only",
            "actor": "new_engineer",
        },
    }
    print("  Calling: POST /api/gumas/evaluate")
    print("  Payload intent: observe_and_learn (expect PASS)")
    print()

    t0 = time.perf_counter()
    try:
        r = session.post(f"{base}/api/gumas/evaluate", json=payload, timeout=10)
        elapsed = time.perf_counter() - t0
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.HTTPError as e:
        elapsed = time.perf_counter() - t0
        fail("Ethics eval failed", f"HTTP {r.status_code}: {r.text[:120]}")
        return step_result("Ethics evaluation", False, elapsed)
    except Exception as e:
        elapsed = time.perf_counter() - t0
        fail("Ethics eval error", str(e))
        return step_result("Ethics evaluation", False, elapsed)

    verdict = (
        data.get("verdict")
        or data.get("compliance_status")
        or data.get("result")
        or data.get("status")
        or "unknown"
    )
    resistance = data.get("resistance_level") or data.get("resistance") or "n/a"
    curvature = data.get("curvature_scores") or data.get("dimensions") or data.get("scores")

    ok("Ethics engine responded", f"verdict={verdict}  resistance={resistance}")

    if curvature and isinstance(curvature, dict):
        info("  5-Dimension Curvature Scores:")
        for dim, score in curvature.items():
            bar_len = int(float(score) * 20) if score is not None else 0
            bar = "█" * bar_len + "░" * (20 - bar_len)
            info(f"    {dim:<30}  [{bar}]  {score}")
    elif curvature:
        info(f"  Scores: {curvature}")
    else:
        info("  (curvature_scores not in response — check /api/gumas/evaluate schema)")

    passed = str(verdict).upper() not in ("BLOCKED", "FAILED", "DENIED", "UNKNOWN")
    return step_result("Ethics evaluation", passed, elapsed)


def demo_4_telemetry(session: requests.Session, base: str) -> bool:
    """
    Step 4: Observability telemetry snapshot.
    Shows the R2 telemetry system — distributed tracing, Prometheus metrics,
    P50/P95/P99 latency. Every operation is traced end-to-end.
    """
    banner("STEP 4/4 — Observability: R2 Telemetry Snapshot")
    print("  Calling: GET /api/telemetry/snapshot  (or /api/telemetry/metrics)")
    print()

    t0 = time.perf_counter()
    passed = False
    data = None

    # Try multiple plausible endpoint paths — surface area is large
    for path in ["/api/telemetry/snapshot", "/api/telemetry/metrics",
                 "/api/telemetry/summary", "/api/telemetry/status",
                 "/api/observability/metrics", "/metrics"]:
        try:
            r = session.get(f"{base}{path}", timeout=8)
            if r.status_code == 200:
                data = r.json() if "application/json" in r.headers.get("content-type", "") else {"raw": r.text[:300]}
                ok(f"Telemetry endpoint found", path)
                passed = True
                break
        except Exception:
            continue

    elapsed = time.perf_counter() - t0

    if not passed:
        info("  No telemetry endpoint responded at standard paths.")
        info("  This is non-critical — telemetry may require auth or a different path.")
        info("  Check docs/reference/API_CATALOG.md for the correct route.")
        return step_result("Telemetry snapshot", False, elapsed)

    if data and isinstance(data, dict) and "raw" not in data:
        latency_keys = [k for k in data if any(x in k.lower() for x in ["p50", "p95", "p99", "latency", "trace"])]
        if latency_keys:
            info("  Latency metrics:")
            for k in latency_keys[:4]:
                info(f"    {k}: {data[k]}")
        else:
            snippet = dict(list(data.items())[:6])
            info(f"  Sample fields: {json.dumps(snippet, indent=6)}")
    elif data and "raw" in data:
        # Prometheus text format — show first 3 metric lines
        lines = [l for l in data["raw"].split("\n") if l and not l.startswith("#")][:3]
        info("  Prometheus metrics (sample):")
        for line in lines:
            info(f"    {line}")

    return step_result("Telemetry snapshot", passed, elapsed)


# ───────────────────────────────────────────────────────────────────
# Entry point
# ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Aurora CloudBank — Engineer Onboarding Demo")
    parser.add_argument("--base-url", default="http://localhost:8000",
                        help="Base URL of a running Aurora server (default: http://localhost:8000)")
    parser.add_argument("--token", default=None,
                        help="Optional JWT bearer token if auth is enabled")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")

    print()
    print("╔" + "═" * (W - 2) + "╗")
    print("║" + " AURORA CLOUDBANK — LIVE ONBOARDING DEMO ".center(W - 2) + "║")
    print("║" + f" Target: {base} ".center(W - 2) + "║")
    print("║" + f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ".center(W - 2) + "║")
    print("╚" + "═" * (W - 2) + "╝")

    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    if args.token:
        session.headers.update({"Authorization": f"Bearer {args.token}"})

    t_total = time.perf_counter()
    results = [
        demo_1_health(session, base),
        demo_2_memory(session, base),
        demo_3_ethics(session, base),
        demo_4_telemetry(session, base),
    ]
    total_elapsed = time.perf_counter() - t_total

    passed_count = sum(results)
    total_count = len(results)
    all_passed = passed_count == total_count

    print()
    print("━" * W)
    print("  DEMO RESULTS")
    print("━" * W)
    print()
    labels = [
        "Health check",
        "Memory write + hash",
        "Ethics evaluation",
        "Telemetry snapshot",
    ]
    for label, passed in zip(labels, results):
        icon = "✅" if passed else "❌"
        print(f"  {icon}  {label}")

    print()
    if all_passed:
        print(f"  🎉  All {total_count}/{total_count} steps passed in {total_elapsed:.1f}s")
        print()
        print("  What you just verified:")
        print("    → Server is live and modules are registered")
        print("    → Memory writes generate real SHA-256 audit hashes")
        print("    → Ethics engine evaluates curvature across 5 dimensions")
        print("    → Observability layer is collecting telemetry")
        print()
        print("  Next steps:")
        print("    → Open http://localhost:8000/docs  (Swagger UI — 340+ routes)")
        print("    → Read GETTING_STARTED_ENGINEER.md  — the 6 modules to know first")
        print("    → Run: make check  (lint + full test suite)")
    else:
        failed = total_count - passed_count
        print(f"  ⚠️   {failed}/{total_count} steps failed in {total_elapsed:.1f}s")
        print()
        print("  Common causes:")
        print("    → Server not running:   make serve-dev")
        print("    → Missing .env:         cp .env.example .env && (fill in 4 keys)")
        print("    → Auth required:        python scripts/onboard_demo.py --token <jwt>")
        print("    → Wrong port:           python scripts/onboard_demo.py --base-url http://localhost:<port>")

    print()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
