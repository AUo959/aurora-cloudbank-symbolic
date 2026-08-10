"""Machine-checkable provenance for CloudBank's CanonRec mirrors/projections."""

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

    def test_staff_registry_authority_boundary_is_resolved(self) -> None:
        receipt = load_provenance()
        staff = next(
            item
            for item in receipt["resolved_surfaces"]
            if item["name"] == "orion_station_staff_registry"
        )

        self.assertEqual(staff["status"], "resolved_authority_boundary")
        self.assertEqual(staff["authority_repository"], "AUo959/CanonRec")
        self.assertRegex(staff["authority_revision"], r"\A[0-9a-f]{40}\Z")
        self.assertEqual(staff["cloudbank_role"], "runtime_projection_non_authoritative")
        self.assertEqual(
            sha256_file(PROJECT_ROOT / staff["cloudbank_path"]),
            staff["cloudbank_sha256"],
        )
        self.assertNotEqual(staff["canonrec_sha256"], staff["cloudbank_sha256"])
        self.assertIn("CanonRec controls canon authority", staff["conflict_policy"])

    def test_no_surface_remains_blocked_on_owner_staff_authority_decision(self) -> None:
        receipt = load_provenance()

        self.assertEqual(receipt["unreconciled_surfaces"], [])

    def test_orbital_locus_authority_boundary_is_narrowly_resolved(self) -> None:
        receipt = load_provenance()
        locus = next(
            item
            for item in receipt["resolved_surfaces"]
            if item["name"] == "orion_station_orbital_locus"
        )

        self.assertEqual(
            locus["status"],
            "resolved_siting_class_exact_point_unresolved",
        )
        self.assertEqual(locus["authority_repository"], "AUo959/CanonRec")
        self.assertRegex(locus["authority_revision"], r"\A[0-9a-f]{40}\Z")
        self.assertEqual(
            sha256_file(PROJECT_ROOT / locus["cloudbank_path"]),
            locus["cloudbank_sha256"],
        )
        self.assertIn("Lagrange point", locus["resolved_claim"])
        self.assertIn("Exact libration point", locus["remaining_uncertainty"])
