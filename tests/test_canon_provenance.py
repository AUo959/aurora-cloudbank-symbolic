"""Machine-checkable provenance for CloudBank's CanonRec mirror."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_PATH = PROJECT_ROOT / "config" / "canon_provenance.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_provenance() -> dict:
    return json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))


@pytest.mark.critical
class TestCanonProvenance(unittest.TestCase):
    def test_canonrec_authority_receipt_is_specific(self) -> None:
        receipt = load_provenance()
        authority = receipt["authority"]

        self.assertEqual(receipt["schema_version"], 1)
        self.assertEqual(authority["repository"], "https://github.com/AUo959/CanonRec")
        self.assertRegex(authority["revision"], r"\A[0-9a-f]{40}\Z")
        self.assertEqual(authority["source_path"], "canon/L3/canonical_validation.yaml")
        self.assertRegex(authority["source_sha256"], r"\A[0-9a-f]{64}\Z")

    def test_checked_in_canon_mirror_matches_provenance_hash(self) -> None:
        receipt = load_provenance()
        mirror = receipt["cloudbank_mirror"]
        mirror_path = PROJECT_ROOT / mirror["path"]

        self.assertTrue(mirror_path.is_file())
        self.assertEqual(sha256_file(mirror_path), mirror["sha256"])
        self.assertEqual(mirror["sha256"], receipt["authority"]["source_sha256"])
        self.assertFalse(mirror["requires_canonrec_checkout_at_runtime"])

    def test_unreconciled_staff_registry_drift_is_explicit(self) -> None:
        receipt = load_provenance()
        staff = next(
            item
            for item in receipt["unreconciled_surfaces"]
            if item["name"] == "orion_station_staff_registry"
        )

        self.assertEqual(staff["status"], "owner_authority_decision_required")
        self.assertEqual(
            sha256_file(PROJECT_ROOT / staff["cloudbank_path"]),
            staff["cloudbank_sha256"],
        )
        self.assertNotEqual(staff["canonrec_sha256"], staff["cloudbank_sha256"])
