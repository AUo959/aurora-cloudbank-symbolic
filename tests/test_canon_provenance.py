"""Machine-checkable provenance for CloudBank's CanonRec mirror."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_PATH = PROJECT_ROOT / "config" / "canon_provenance.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_provenance() -> dict:
    return json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))


@pytest.mark.critical
def test_canonrec_authority_receipt_is_specific() -> None:
    receipt = load_provenance()
    authority = receipt["authority"]

    assert receipt["schema_version"] == 1
    assert authority["repository"] == "https://github.com/AUo959/CanonRec"
    assert re.fullmatch(r"[0-9a-f]{40}", authority["revision"])
    assert authority["source_path"] == "canon/L3/canonical_validation.yaml"
    assert re.fullmatch(r"[0-9a-f]{64}", authority["source_sha256"])


@pytest.mark.critical
def test_checked_in_canon_mirror_matches_provenance_hash() -> None:
    receipt = load_provenance()
    mirror = receipt["cloudbank_mirror"]
    mirror_path = PROJECT_ROOT / mirror["path"]

    assert mirror_path.is_file()
    assert sha256_file(mirror_path) == mirror["sha256"]
    assert mirror["sha256"] == receipt["authority"]["source_sha256"]
    assert mirror["requires_canonrec_checkout_at_runtime"] is False


@pytest.mark.critical
def test_unreconciled_staff_registry_drift_is_explicit() -> None:
    receipt = load_provenance()
    staff = next(
        item
        for item in receipt["unreconciled_surfaces"]
        if item["name"] == "orion_station_staff_registry"
    )

    assert staff["status"] == "owner_authority_decision_required"
    assert sha256_file(PROJECT_ROOT / staff["cloudbank_path"]) == staff["cloudbank_sha256"]
    assert staff["canonrec_sha256"] != staff["cloudbank_sha256"]
