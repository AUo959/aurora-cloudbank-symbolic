"""Unit tests for the shared helpers extracted by the complexity cleanup.

The refactor kept every public outcome identical; these tests pin the helper
semantics that the extracted predicates rely on. Synthetic L2 only.
"""
from __future__ import annotations

import unittest

from simulation.runtime.gumas_unified import CausalEngine
from simulation.runtime.gumas_unified.external_evidence import (
    canonical_sha256, digest_without, fields_match, is_synthetic_engine,
)
from simulation.runtime.gumas_unified.kernel import _deliver_scheduled
from simulation.runtime.gumas_unified.model import ScheduledEvent, is_sha256_hex
from simulation.runtime.gumas_unified.scenario import fixture


class FieldsMatchTests(unittest.TestCase):
    def test_boolean_requirements_are_identity_checks(self):
        self.assertTrue(fields_match({"a": False}, {"a": False}))
        self.assertFalse(fields_match({"a": 0}, {"a": False}))
        self.assertFalse(fields_match({"a": 1}, {"a": True}))
        self.assertFalse(fields_match({}, {"a": False}))

    def test_other_requirements_use_equality(self):
        self.assertTrue(fields_match({"n": 1, "s": "x"}, {"n": 1, "s": "x"}))
        self.assertTrue(fields_match({"n": True}, {"n": 1}))
        self.assertFalse(fields_match({"s": "y"}, {"s": "x"}))
        self.assertFalse(fields_match({}, {"s": "x"}))

    def test_empty_requirement_matches(self):
        self.assertTrue(fields_match({}, {}))


class DigestAndShapeTests(unittest.TestCase):
    def test_digest_without_excludes_only_named_field(self):
        payload = {"a": 1, "b": 2, "self_sha256": "ignored"}
        self.assertEqual(digest_without(payload, "self_sha256"),
                         canonical_sha256({"a": 1, "b": 2}))
        self.assertNotEqual(digest_without(payload, "a"),
                            digest_without(payload, "self_sha256"))

    def test_is_sha256_hex(self):
        self.assertTrue(is_sha256_hex("0" * 64))
        self.assertTrue(is_sha256_hex("abcdef0123456789" * 4))
        for bad in ("0" * 63, "0" * 65, "A" * 64, "g" * 64, None, 0, b"0" * 64):
            self.assertFalse(is_sha256_hex(bad), bad)


class SyntheticEngineTests(unittest.TestCase):
    def test_requires_engine_with_synthetic_run_id(self):
        self.assertTrue(is_synthetic_engine(CausalEngine(fixture(), run_id="synthetic-h")))
        self.assertFalse(is_synthetic_engine(object()))
        self.assertFalse(is_synthetic_engine(None))


class SchedulerDispatchTests(unittest.TestCase):
    def test_unknown_event_kind_is_refused_after_claim(self):
        world = fixture()
        event = ScheduledEvent("scheduled-x", world.time_s, 0, "not_a_kind", {})
        world.pending.append(event)
        with self.assertRaisesRegex(AssertionError, "unsupported scheduled event"):
            _deliver_scheduled(world, event)
        self.assertEqual(world.pending, [])

    def test_missing_event_is_refused(self):
        world = fixture()
        event = ScheduledEvent("scheduled-x", world.time_s, 0, "cargo_arrival", {})
        with self.assertRaisesRegex(AssertionError, "missing or duplicated"):
            _deliver_scheduled(world, event)


if __name__ == "__main__":
    unittest.main()
