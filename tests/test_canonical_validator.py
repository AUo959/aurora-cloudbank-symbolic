"""Regression tests for canonical validation auto-fixes."""

from __future__ import annotations

import unittest
from pathlib import Path
import shutil

from scripts.canonical_validator import CanonicalValidator


CHECKS = unittest.TestCase()


def test_staff_name_validation_preserves_python_identifiers(tmp_path: Path) -> None:
    """Canonical display-name fixes must not rewrite snake-case Python identifiers."""

    source_path = tmp_path / "agent_contract.py"
    original = 'AGENT_ID = "alex_thorne"\n'
    source_path.write_text(original)

    results = CanonicalValidator().validate_file(str(source_path))

    CHECKS.assertEqual(source_path.read_text(), original)
    CHECKS.assertFalse(any(result.status == "AUTO_FIXED" for result in results))


def test_canonical_validator_does_not_rewrite_its_own_source(tmp_path: Path) -> None:
    """Endpoint checks must leave already-canonical validator source unchanged."""

    source_path = Path(__file__).resolve().parents[1] / "scripts" / "canonical_validator.py"
    copied_path = tmp_path / source_path.name
    shutil.copyfile(source_path, copied_path)
    original = copied_path.read_text()

    results = CanonicalValidator().validate_file(str(copied_path))

    CHECKS.assertEqual(copied_path.read_text(), original)
    CHECKS.assertFalse(any(result.status == "AUTO_FIXED" for result in results))
