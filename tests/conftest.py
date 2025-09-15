"""
Aurora/GUMAS: Pytest session entropy seal and DLP-aware metadata export.

Conventions:
- T1: temporal anchoring of test session
- SRB: spatial-relational boundary tag for CI node context
- DLP: mark test exports as non-confidential by default (override per module if needed)
- Ethics protocol: Picard_Delta_3
- Active anchor seed: EOS_SEED_ORION

Outputs:
- artifacts/manifest/pytest-entropy-seal.json (session anchors, entropy hints, SHA seals)
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import secrets
import time
from datetime import datetime, timezone
from typing import Dict, Iterator

import pytest


def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


@pytest.fixture(scope="session", autouse=True)
def entropy_seal() -> Iterator[Dict[str, str]]:
    """
    Autouse session fixture that:
    - Generates a high-entropy session seed and captures environment anchors.
    - Writes a DLP-aware manifest early for continuity even on early failures.
    - On teardown, records elapsed_seconds for drift checks.
    """
    seed_bytes = secrets.token_bytes(32)
    seed_hex = seed_bytes.hex()
    commit = os.getenv("GITHUB_SHA", "local-dev")
    repo = os.getenv("GITHUB_REPOSITORY", "local-dev/aurora-cloudbank-symbolic")
    node = platform.node()
    ts = datetime.now(timezone.utc).isoformat()

    manifest = {
        "anchor_seed": "EOS_SEED_ORION",
        "tags": ["T1", "SRB_TICK", "ANCHOR_LOCKED"],
        "dlp": {
            "level": "DLP_L1_OK",
            "symbolic_hash_validation": True,
            "notes": "Pytest session export; non-confidential.",
        },
        "session": {
            "entropy_seed_sha256": _sha256_bytes(seed_bytes),
            "entropy_seed_hint": f"{seed_hex[:8]}...{seed_hex[-8:]}",  # non-reversible hint
            "pid": os.getpid(),
            "node": node,
            "started_at": ts,
        },
        "build": {"repo": repo, "commit": commit},
        "version": "pytest.entropy.v1",
        "ethics_protocol": "Picard_Delta_3",
        "notes": "Session-level entropy seal for traceability and drift checks.",
    }

    out_dir = os.path.join("artifacts", "manifest")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "pytest-entropy-seal.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    yield manifest

    # Update with end time and basic drift measure (elapsed seconds)
    try:
        start_iso = manifest["session"]["started_at"]
        start_ts = datetime.fromisoformat(start_iso).timestamp()
        elapsed = max(0.0, time.time() - start_ts)
        manifest["session"]["elapsed_seconds"] = round(elapsed, 6)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
    except Exception:
        # Divergent Truths: do not fail tests for sealing update errors; log for review.
        pass
