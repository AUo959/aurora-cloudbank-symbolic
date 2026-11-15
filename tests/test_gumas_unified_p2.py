"""P2 acceptance tests: governed fixture identity and exact time coordinates."""
from __future__ import annotations

from copy import deepcopy
import unittest

from simulation.runtime.gumas_unified import CausalEngine
from simulation.runtime.gumas_unified.bindings import (
    identity_binding_view, prepare_fixture_identity_binding,
)
from simulation.runtime.gumas_unified.external_evidence import (
    EvidenceError, canonical_sha256, observe_ace_identity,
    observe_phase9_ledger,
)
from simulation.runtime.gumas_unified.scenario import fixture
from simulation.runtime.gumas_unified.time_alignment import (
    operator_cross_scale_frame, prepare_fixture_clock_anchor,
    project_tactical_interval,
)


def ace_projection(entity_id: str = "fixture_archivist") -> dict:
    world = {
        "world_id": "fixture_ace_sandbox",
        "world_scope": "isolated_aurora_world",
        "status": "ready",
        "canonical_workspace_authority": False,
        "canon_head": "a" * 40,
        "sources": {
            "root": {"commit": "b" * 40},
            "CanonRec": {"commit": "c" * 40},
            "aurora-cloudbank-symbolic-main": {"commit": "d" * 40},
        },
    }
    response = {
        "world_id": "fixture_ace_sandbox",
        "world_scope": "isolated_aurora_world",
        "request_id": "fixture-read-001",
        "operation": "retrieve",
        "status": "RETRIEVED_CANON",
        "determination_id": "fixture-determination-001",
        "entity_id": entity_id,
        "character": {
            "canonical_id": entity_id,
            "name": f"Fixture {entity_id}",
            "background": "Private narrative must not appear in bindings.",
        },
        "origin": "sandbox_created",
        "packet_ref": "/private/fixture/packet",
    }
    return observe_ace_identity(world, response)


def tactical_projection() -> dict:
    import hashlib

    def sha(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    row = {
        "schema": "aurora://simulation/gumas/phase9_ledger_entry/v1.0",
        "phase9_contract_id": "GUMAS_LIVE_OBSERVATION_ORCHESTRATOR_LEDGER_v1_0",
        "phase9_version": "1.0.0",
        "canonical_json_profile": "aurora-canonical-json-v1",
        "historical_canon_status": "non_canon_simulation_instance",
        "phase9_source_identity": {"source_sha256": sha("phase9-source")},
        "accepted_source_identities": {
            "phase9_orchestrator": {"source_sha256": sha("phase9-source")},
        },
        "run_identity_sha256": sha("synthetic-tactical-run"),
        "t0_roster_sha256": sha("synthetic-roster"),
        "macrostep_index": 1,
        "start_elapsed_ms": 0,
        "end_elapsed_ms": 425,
        "previous_ledger_entry_sha256": "GENESIS",
        "previous_committed_state_sha256": sha("synthetic-T0"),
        "live_observation_sha256_by_side": {
            "a": sha("observation-a"), "b": sha("observation-b"),
        },
        "live_observation_receipt_sha256_by_side": {
            "a": sha("receipt-a"), "b": sha("receipt-b"),
        },
        "phase4_decision_sha256_by_fleet": {
            "fleet-a": sha("decision-a"), "fleet-b": sha("decision-b"),
        },
        "phase5_state_sha256": sha("phase5-state"),
        "phase5_receipt_sha256": sha("phase5-receipt"),
        "phase6_state_sha256": sha("phase6-state"),
        "phase6_receipt_sha256": sha("phase6-receipt"),
        "phase7_state_sha256": sha("phase7-state"),
        "phase7_receipt_sha256": sha("phase7-receipt"),
        "phase8_next_state_sha256": sha("phase8-state"),
        "phase8_resolution_state_sha256": sha("phase8-resolution"),
        "phase8_receipt_sha256": sha("phase8-receipt"),
        "terminal_outcome": {"termination_mode": "ongoing"},
        "reporter_invoked": False,
        "run0_executed": False,
    }
    row["ledger_entry_sha256"] = canonical_sha256(row)
    return observe_phase9_ledger([row])


def binding_grant(engine: CausalEngine, ace: dict, actor_id: str = "governor",
                  *, valid_for_s: int = 20) -> dict:
    state = engine.state
    return {
        "schema": "gumas.unified.fixture_binding_grant.p2",
        "operation": "bind_fixture_identity",
        "scope": "synthetic_fixture_only",
        "grant_ref": "fixture:explicit-binding-001",
        "operator_intent_explicit": True,
        "run_id": engine.run_id,
        "state_sha256": state.digest(),
        "actor_id": actor_id,
        "site_id": state.actors[actor_id].site_id,
        "world_id": ace["world_id"],
        "entity_id": ace["entity_id"],
        "ace_projection_sha256": ace["projection_sha256"],
        "effective_at_s": state.time_s,
        "valid_until_s": state.time_s + valid_for_s,
        "allow_canon_promotion": False,
        "allow_agent_memory_injection": False,
        "allow_permission_changes": False,
    }


def clock_grant(engine: CausalEngine, tactical: dict) -> dict:
    state = engine.state
    return {
        "schema": "gumas.unified.clock_grant.p2",
        "operation": "map_external_elapsed_ms",
        "scope": "synthetic_fixture_only",
        "grant_ref": "fixture:explicit-clock-assumption",
        "operator_intent_explicit": True,
        "run_id": engine.run_id,
        "local_state_sha256": state.digest(),
        "local_epoch_s": state.time_s,
        "external_projection_sha256": tactical["projection_sha256"],
        "external_run_identity_sha256": tactical["run_identity_sha256"],
        "external_ledger_tail_sha256": tactical["last_ledger_entry_sha256"],
        "reference_frame_id": "fixture:synthetic-shared-frame",
        "rate": "1_ms_per_ms",
        "allow_execution": False,
        "allow_canon_time_promotion": False,
    }


class UnifiedP2Tests(unittest.TestCase):
    def make_engine(self) -> CausalEngine:
        return CausalEngine(fixture(), run_id="synthetic-p2")

    def test_granted_fixture_binding_is_committed_in_one_kernel_ledger(self):
        engine = self.make_engine()
        ace = ace_projection()
        grant = binding_grant(engine, ace)
        before_actor = engine.actor_view("governor")
        before_totals = engine.state.totals()
        receipt = engine.bind_fixture_identity(ace, grant)
        self.assertEqual(receipt.kind, "fixture_identity_bound")
        self.assertEqual(len(engine.ledger), 1)
        self.assertEqual(receipt.effect["entity_id"], "fixture_archivist")
        self.assertEqual(engine.state.totals(), before_totals)
        self.assertEqual(engine.actor_view("governor"), before_actor)
        self.assertEqual(engine.state.identity_bindings["governor"]["world_id"],
                         "fixture_ace_sandbox")
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_p2_identity_view_is_synthetic_and_private(self):
        engine = self.make_engine()
        ace = ace_projection()
        engine.bind_fixture_identity(ace, binding_grant(engine, ace))
        view = identity_binding_view(engine, "governor")
        self.assertTrue(view["active_at_current_time"])
        self.assertFalse(view["source_canon_promoted"])
        self.assertFalse(view["permissions_changed"])
        self.assertFalse(view["agent_memory_injected"])
        self.assertFalse(view["external_identity_authenticated"])
        self.assertNotIn("background", str(engine.evidence()))
        self.assertNotIn("Private narrative", str(view))
        self.assertEqual(engine.state.actors["governor"].authorized_dispatch_sites,
                         ("union_depot",))

    def test_bindings_expire_without_rewriting_history(self):
        engine = self.make_engine()
        ace = ace_projection()
        engine.bind_fixture_identity(ace, binding_grant(engine, ace, valid_for_s=3))
        self.assertTrue(identity_binding_view(engine, "governor")["active_at_current_time"])
        engine.advance_to(3)
        self.assertFalse(identity_binding_view(engine, "governor")["active_at_current_time"])
        self.assertEqual(engine.ledger[0].kind, "fixture_identity_bound")
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_stale_state_binding_refuses_atomically(self):
        engine = self.make_engine()
        ace = ace_projection()
        grant = binding_grant(engine, ace)
        engine.advance_to(2)
        before, receipts = engine.state.digest(), engine.ledger
        with self.assertRaisesRegex(EvidenceError, "anchored"):
            engine.bind_fixture_identity(ace, grant)
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.ledger, receipts)

    def test_mismatched_actor_site_and_source_refuse(self):
        engine = self.make_engine()
        ace = ace_projection()
        for field, replacement in (
            ("site_id", "frontier_port"),
            ("actor_id", "missing"),
            ("world_id", "another-world"),
            ("entity_id", "another-entity"),
            ("ace_projection_sha256", "f" * 64),
        ):
            bad = binding_grant(engine, ace)
            bad[field] = replacement
            before = engine.state.digest()
            with self.assertRaises(EvidenceError):
                engine.bind_fixture_identity(ace, bad)
            self.assertEqual(engine.state.digest(), before)
            self.assertEqual(engine.ledger, [])

    def test_source_identity_must_be_checksum_consistent(self):
        engine = self.make_engine()
        ace = ace_projection()
        grant = binding_grant(engine, ace)
        ace["name"] = "Mismatched name"
        with self.assertRaisesRegex(EvidenceError, "checksum"):
            engine.bind_fixture_identity(ace, grant)

    def test_untrusted_grants_do_not_promote_or_inject(self):
        engine = self.make_engine()
        ace = ace_projection()
        for field, value in (
            ("operator_intent_explicit", False),
            ("scope", "source_canon"),
            ("grant_ref", "user:unverified"),
            ("allow_canon_promotion", True),
            ("allow_agent_memory_injection", True),
            ("allow_permission_changes", True),
            ("operation", "create"),
        ):
            bad = binding_grant(engine, ace)
            bad[field] = value
            with self.assertRaises(EvidenceError):
                engine.bind_fixture_identity(ace, bad)
        self.assertEqual(engine.ledger, [])

    def test_binding_duplicate_actor_and_entity_refused(self):
        engine = self.make_engine()
        ace = ace_projection()
        engine.bind_fixture_identity(ace, binding_grant(engine, ace))
        before = engine.state.digest()
        with self.assertRaises(EvidenceError):
            engine.bind_fixture_identity(ace, binding_grant(engine, ace))
        with self.assertRaisesRegex(EvidenceError, "already bound"):
            engine.bind_fixture_identity(
                ace, binding_grant(engine, ace, actor_id="local_dissenter"))
        self.assertEqual(engine.state.digest(), before)

    def test_independent_identities_can_bind_distinct_actors(self):
        engine = self.make_engine()
        first, second = ace_projection(), ace_projection("second_archivist")
        engine.bind_fixture_identity(first, binding_grant(engine, first))
        engine.bind_fixture_identity(
            second, binding_grant(engine, second, actor_id="local_dissenter"))
        self.assertEqual(len(engine.state.identity_bindings), 2)
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_binding_replays_same_inputs_exactly(self):
        a, b = self.make_engine(), self.make_engine()
        ace = ace_projection()
        for engine in (a, b):
            engine.bind_fixture_identity(ace, binding_grant(engine, ace))
            engine.advance_to(2)
        self.assertEqual(a.evidence(), b.evidence())

    def test_bindings_are_not_writable_through_snapshots(self):
        engine = self.make_engine()
        ace = ace_projection()
        receipt = engine.bind_fixture_identity(ace, binding_grant(engine, ace))
        receipt.effect["entity_id"] = "tampered"
        public = engine.state
        public.identity_bindings["governor"]["entity_id"] = "tampered"
        self.assertEqual(identity_binding_view(engine, "governor")["entity_id"],
                         "fixture_archivist")
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_initial_unvalidated_identity_binding_is_rejected(self):
        world = fixture()
        world.identity_bindings["governor"] = {"entity_id": "forged"}
        with self.assertRaises(ValueError):
            CausalEngine(world)

    def test_millisecond_clock_mapping_preserves_fractional_seconds(self):
        engine = self.make_engine()
        engine.advance_to(7)
        tactical = tactical_projection()
        anchor = prepare_fixture_clock_anchor(engine, tactical, clock_grant(engine, tactical))
        before, ledger = engine.state.digest(), engine.ledger
        mapped = project_tactical_interval(engine, tactical, anchor,
                                           start_elapsed_ms=200, end_elapsed_ms=425)
        self.assertEqual(mapped["mapped_start_l2_ms"], 7200)
        self.assertEqual(mapped["mapped_end_l2_ms"], 7425)
        self.assertEqual((mapped["start_l2_second"], mapped["start_subsecond_ms"]),
                         (7, 200))
        self.assertEqual((mapped["end_l2_second"], mapped["end_subsecond_ms"]),
                         (7, 425))
        self.assertFalse(mapped["physical_causality_verified"])
        self.assertFalse(mapped["kernel_clock_advanced"])
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.ledger, ledger)

    def test_time_anchor_refuses_any_unapproved_execution_claim(self):
        engine = self.make_engine()
        tactical = tactical_projection()
        for key, value in (
            ("allow_execution", True), ("allow_canon_time_promotion", True),
            ("operator_intent_explicit", False), ("rate", "1_s_per_ms"),
            ("reference_frame_id", "canonical:universe"),
            ("scope", "external_authoritative"),
        ):
            bad = clock_grant(engine, tactical)
            bad[key] = value
            with self.assertRaises(EvidenceError):
                prepare_fixture_clock_anchor(engine, tactical, bad)
        self.assertEqual(engine.ledger, [])

    def test_clock_mapping_rejects_stale_local_anchor(self):
        engine = self.make_engine()
        tactical = tactical_projection()
        anchor = prepare_fixture_clock_anchor(engine, tactical, clock_grant(engine, tactical))
        engine.advance_to(1)
        with self.assertRaisesRegex(EvidenceError, "stale"):
            project_tactical_interval(engine, tactical, anchor,
                                      start_elapsed_ms=0, end_elapsed_ms=425)

    def test_clock_anchor_rejects_mismatched_run_and_source(self):
        engine = self.make_engine()
        tactical = tactical_projection()
        for field, value in (
            ("run_id", "synthetic-another"),
            ("external_projection_sha256", "f" * 64),
            ("external_run_identity_sha256", "f" * 64),
            ("external_ledger_tail_sha256", "f" * 64),
        ):
            bad = clock_grant(engine, tactical)
            bad[field] = value
            with self.assertRaises(EvidenceError):
                prepare_fixture_clock_anchor(engine, tactical, bad)

    def test_clock_intervals_refuse_out_of_range_or_non_integer(self):
        engine = self.make_engine()
        tactical = tactical_projection()
        anchor = prepare_fixture_clock_anchor(engine, tactical, clock_grant(engine, tactical))
        for start, end in ((0, 426), (200, 200), (300, 200),
                           (-1, 200), (False, 200), (0, 425.5)):
            with self.assertRaises(EvidenceError):
                project_tactical_interval(engine, tactical, anchor,
                                          start_elapsed_ms=start, end_elapsed_ms=end)

    def test_tactical_projection_forgery_rejected_even_if_rehashed(self):
        engine = self.make_engine()
        tactical = tactical_projection()
        grant = clock_grant(engine, tactical)
        tactical["source_authenticated"] = True
        tactical["projection_sha256"] = canonical_sha256({
            k: v for k, v in tactical.items() if k != "projection_sha256"
        })
        with self.assertRaises(EvidenceError):
            prepare_fixture_clock_anchor(engine, tactical, grant)

    def test_cross_scale_operator_view_is_not_agent_knowledge(self):
        engine = self.make_engine()
        engine.advance_to(7)
        ace, tactical = ace_projection(), tactical_projection()
        engine.bind_fixture_identity(ace, binding_grant(engine, ace))
        anchor = prepare_fixture_clock_anchor(engine, tactical,
                                              clock_grant(engine, tactical))
        before, events = engine.state.digest(), engine.ledger
        frame = operator_cross_scale_frame(
            engine, "governor", tactical, anchor,
            start_elapsed_ms=0, end_elapsed_ms=425)
        self.assertEqual(frame["identity"]["entity_id"], "fixture_archivist")
        self.assertEqual(frame["tactical_interval"]["mapped_end_l2_ms"], 7425)
        self.assertTrue(frame["identity_binding_in_kernel"])
        self.assertFalse(frame["tactical_execution_authorized"])
        self.assertFalse(frame["tactical_effects_imported"])
        self.assertFalse(frame["canon_mutation_permitted"])
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.ledger, events)
        self.assertEqual(engine.actor_view("governor")["received_reports"], [])

    def test_cross_scale_view_refuses_expired_bindings(self):
        engine = self.make_engine()
        ace, tactical = ace_projection(), tactical_projection()
        engine.bind_fixture_identity(ace, binding_grant(engine, ace, valid_for_s=1))
        engine.advance_to(1)
        anchor = prepare_fixture_clock_anchor(engine, tactical, clock_grant(engine, tactical))
        with self.assertRaisesRegex(EvidenceError, "expired"):
            operator_cross_scale_frame(
                engine, "governor", tactical, anchor,
                start_elapsed_ms=0, end_elapsed_ms=425)


if __name__ == "__main__":
    unittest.main()
