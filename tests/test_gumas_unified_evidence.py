"""P1 cross-repository evidence-adapter tests: pure, synthetic, fail-closed."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import unittest

from simulation.runtime.gumas_unified.external_evidence import (
    EvidenceError, canonical_sha256, observe_ace_identity,
    observe_phase9_acceptance, observe_phase9_ledger, operator_evidence_frame,
)
from simulation.runtime.gumas_unified.kernel import CausalEngine
from simulation.runtime.gumas_unified.scenario import fixture


def sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def ace_status() -> dict:
    return {
        "world_id": "sandbox-evidence-world",
        "world_scope": "isolated_aurora_world",
        "status": "ready",
        "canonical_workspace_authority": False,
        "canon_head": "a" * 40,
        "sources": {
            "root": {"path": "/private/sensitive/root", "commit": "b" * 40},
            "CanonRec": {"path": "/private/sensitive/CanonRec", "commit": "c" * 40},
            "aurora-cloudbank-symbolic-main": {
                "path": "/private/sensitive/CloudBank", "commit": "d" * 40
            },
        },
        "pending_requests": [],
    }


def ace_retrieval() -> dict:
    return {
        "world_id": "sandbox-evidence-world",
        "world_scope": "isolated_aurora_world",
        "request_id": "read-001",
        "operation": "retrieve",
        "status": "RETRIEVED_CANON",
        "determination_id": "determination-read-001",
        "entity_id": "fixture_archivist",
        "character": {
            "canonical_id": "fixture_archivist",
            "name": "Fixture Archivist",
            "background": "A background that must NOT leak through this projection.",
        },
        "origin": "sandbox_created",
        "packet_ref": "/private/record/that/must/not/leak",
        "materialization": {"secret": "do not include"},
    }


def phase9_entry(index: int = 1, previous: dict | None = None,
                 *, terminal_mode: str = "ongoing") -> dict:
    starting = 0 if previous is None else previous["end_elapsed_ms"]
    row = {
        "schema": "aurora://simulation/gumas/phase9_ledger_entry/v1.0",
        "phase9_contract_id": "GUMAS_LIVE_OBSERVATION_ORCHESTRATOR_LEDGER_v1_0",
        "phase9_version": "1.0.0",
        "canonical_json_profile": "aurora-canonical-json-v1",
        "historical_canon_status": "non_canon_simulation_instance",
        "phase9_source_identity": {"source_sha256": sha("phase9-source")},
        "accepted_source_identities": {
            "phase9_orchestrator": {"source_sha256": sha("phase9-source")}
        },
        "run_identity_sha256": sha("tactical-run"),
        "t0_roster_sha256": sha("t0-roster"),
        "macrostep_index": index,
        "start_elapsed_ms": starting,
        "end_elapsed_ms": starting + 200,
        "previous_ledger_entry_sha256":
            "GENESIS" if previous is None else previous["ledger_entry_sha256"],
        "previous_committed_state_sha256":
            sha("initial-state") if previous is None
            else previous["phase8_next_state_sha256"],
        "live_observation_sha256_by_side": {
            "left": sha(f"left-obs-{index}"),
            "right": sha(f"right-obs-{index}"),
        },
        "live_observation_receipt_sha256_by_side": {
            "left": sha(f"left-rec-{index}"),
            "right": sha(f"right-rec-{index}"),
        },
        "phase4_decision_sha256_by_fleet": {
            "fleet_left": sha(f"fleet-left-{index}"),
            "fleet_right": sha(f"fleet-right-{index}"),
        },
        "phase5_state_sha256": sha(f"phase5-state-{index}"),
        "phase5_receipt_sha256": sha(f"phase5-rec-{index}"),
        "phase6_state_sha256": sha(f"phase6-state-{index}"),
        "phase6_receipt_sha256": sha(f"phase6-rec-{index}"),
        "phase7_state_sha256": sha(f"phase7-state-{index}"),
        "phase7_receipt_sha256": sha(f"phase7-rec-{index}"),
        "phase8_next_state_sha256": sha(f"phase8-next-{index}"),
        "phase8_resolution_state_sha256": sha(f"phase8-res-{index}"),
        "phase8_receipt_sha256": sha(f"phase8-rec-{index}"),
        "terminal_outcome": {"termination_mode": terminal_mode},
        "reporter_invoked": False,
        "run0_executed": False,
    }
    row["ledger_entry_sha256"] = canonical_sha256(row)
    return row


def rehash(row: dict) -> dict:
    row["ledger_entry_sha256"] = canonical_sha256({
        k: v for k, v in row.items() if k != "ledger_entry_sha256"
    })
    return row


def phase9_acceptance() -> dict:
    return {
        "receipt_id": "GUMAS-PHASE9-LIVE-OBSERVATION-ORCHESTRATOR-LEDGER-ACCEPTANCE-2026-08-15",
        "phase": 9,
        "status": "PASS",
        "historical_canon_status": "non_canon_simulation_instance",
        "run0_executed": False,
        "run0_remains_blocked": True,
        "contract": {
            "contract_id": "GUMAS_LIVE_OBSERVATION_ORCHESTRATOR_LEDGER_v1_0",
            "version": "1.0.0",
        },
        "accepted_one_step_witness": {
            "macrosteps_executed": 1,
            "ledger_entry_sha256": sha("witness-ledger"),
            "run_identity_sha256": sha("witness-run"),
            "t0_roster_sha256": sha("witness-roster"),
            "source_t0_sha256": sha("witness-t0"),
            "reporter_invoked": False,
            "run0_executed": False,
        },
    }


class P1EvidenceTests(unittest.TestCase):
    def test_ace_read_only_identity_from_same_world(self):
        status, retrieved = ace_status(), ace_retrieval()
        before = deepcopy((status, retrieved))
        observed = observe_ace_identity(status, retrieved)
        self.assertEqual((status, retrieved), before)
        self.assertEqual(observed["entity_id"], "fixture_archivist")
        self.assertEqual(observed["origin"], "sandbox_created")
        self.assertFalse(observed["identity_bound_to_l2_actor"])
        self.assertFalse(observed["source_canon_promoted"])
        self.assertEqual(len(observed["source_pins"]), 3)
        self.assertEqual(observed["projection_sha256"],
                         canonical_sha256({k: v for k, v in observed.items()
                                          if k != "projection_sha256"}))
        self.assertNotIn("background", str(observed))
        self.assertNotIn("/private/", str(observed))
        self.assertNotIn("secret", str(observed))

    def test_ace_rejects_cross_world_and_identity_alias(self):
        status, retrieved = ace_status(), ace_retrieval()
        retrieved["world_id"] = "other-world"
        with self.assertRaises(EvidenceError):
            observe_ace_identity(status, retrieved)
        retrieved["world_id"] = status["world_id"]
        retrieved["character"]["canonical_id"] = "someone-else"
        with self.assertRaises(EvidenceError):
            observe_ace_identity(status, retrieved)

    def test_ace_rejects_unapproved_create_preview_and_pending_world(self):
        status, retrieved = ace_status(), ace_retrieval()
        for operation in ("create", "preview"):
            q = deepcopy(retrieved)
            q["operation"] = operation
            with self.assertRaises(EvidenceError):
                observe_ace_identity(status, q)
        for state in ("recovery_pending", "unverified"):
            q = deepcopy(status)
            q["status"] = state
            with self.assertRaises(EvidenceError):
                observe_ace_identity(q, retrieved)
        status["canonical_workspace_authority"] = True
        with self.assertRaises(EvidenceError):
            observe_ace_identity(status, retrieved)

    def test_ace_rejects_invalid_pins_and_unresolved_entity(self):
        status, retrieved = ace_status(), ace_retrieval()
        status["sources"]["CanonRec"]["commit"] = "not-a-sha"
        with self.assertRaises(EvidenceError):
            observe_ace_identity(status, retrieved)
        status = ace_status()
        retrieved["status"] = "EXECUTION_BLOCKED"
        with self.assertRaises(EvidenceError):
            observe_ace_identity(status, retrieved)

    def test_phase9_ledger_one_and_two_step_consistency(self):
        first = phase9_entry()
        second = phase9_entry(index=2, previous=first)
        original = deepcopy([first, second])
        result = observe_phase9_ledger([first, second])
        self.assertEqual([first, second], original)
        self.assertEqual(result["phase9_entries_structurally_verified"], 2)
        self.assertEqual(result["elapsed_ms_at_tail"], 400)
        self.assertFalse(result["full_state_replay_verified"])
        self.assertFalse(result["clock_aligned_to_unified"])
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(result["last_ledger_entry_sha256"],
                         second["ledger_entry_sha256"])

    def test_phase9_ledger_tampering_fails_closed(self):
        row = phase9_entry()
        row["phase8_next_state_sha256"] = sha("tampered")
        with self.assertRaisesRegex(EvidenceError, "digest mismatch"):
            observe_phase9_ledger([row])
        row = phase9_entry()
        row["run0_executed"] = True
        rehash(row)
        with self.assertRaises(EvidenceError):
            observe_phase9_ledger([row])
        row = phase9_entry()
        row["reporter_invoked"] = True
        rehash(row)
        with self.assertRaises(EvidenceError):
            observe_phase9_ledger([row])

    def test_phase9_rejects_false_chain_even_with_individually_valid_hashes(self):
        a = phase9_entry()
        b = phase9_entry(2, a)
        b["previous_committed_state_sha256"] = sha("different-predecessor")
        rehash(b)
        with self.assertRaisesRegex(EvidenceError, "linkage"):
            observe_phase9_ledger([a, b])
        b = phase9_entry(2, a)
        b["run_identity_sha256"] = sha("changed-run")
        rehash(b)
        with self.assertRaisesRegex(EvidenceError, "identity drift"):
            observe_phase9_ledger([a, b])
        b = phase9_entry(2, a)
        b["start_elapsed_ms"] = 300
        b["end_elapsed_ms"] = 500
        rehash(b)
        with self.assertRaisesRegex(EvidenceError, "continuity"):
            observe_phase9_ledger([a, b])

    def test_phase9_refuses_continuation_after_terminal_state(self):
        first = phase9_entry(terminal_mode="ceasefire")
        following = phase9_entry(2, first)
        with self.assertRaisesRegex(EvidenceError, "terminal"):
            observe_phase9_ledger([first, following])

    def test_phase9_rejects_missing_fields_wrong_units_and_invalid_json(self):
        row = phase9_entry()
        del row["phase8_receipt_sha256"]
        with self.assertRaises(EvidenceError):
            observe_phase9_ledger([row])
        row = phase9_entry()
        row["end_elapsed_ms"] = -1
        rehash(row)
        with self.assertRaises(EvidenceError):
            observe_phase9_ledger([row])
        row = phase9_entry()
        row["extra_bad_float"] = float("nan")
        with self.assertRaises(EvidenceError):
            observe_phase9_ledger([row])

    def test_phase9_acceptance_is_a_claim_not_a_battle(self):
        receipt = phase9_acceptance()
        original = deepcopy(receipt)
        observed = observe_phase9_acceptance(receipt)
        self.assertEqual(receipt, original)
        self.assertEqual(observed["recorded_status"], "PASS")
        self.assertFalse(observed["claim_cryptographically_authenticated"])
        self.assertFalse(observed["full_state_replay_verified"])
        self.assertTrue(observed["run0_remains_blocked"])
        self.assertNotIn("battle_outcome", observed)

    def test_phase9_acceptance_rejects_run0_claim(self):
        receipt = phase9_acceptance()
        receipt["run0_executed"] = True
        with self.assertRaises(EvidenceError):
            observe_phase9_acceptance(receipt)
        receipt = phase9_acceptance()
        receipt["accepted_one_step_witness"]["macrosteps_executed"] = 12
        with self.assertRaises(EvidenceError):
            observe_phase9_acceptance(receipt)

    def test_operator_context_is_pure_read_only_and_separate_clocks(self):
        engine = CausalEngine(fixture())
        local_before, ledger_before = engine.state.digest(), engine.ledger
        identity = observe_ace_identity(ace_status(), ace_retrieval())
        tactical = observe_phase9_ledger([phase9_entry()])
        acceptance = observe_phase9_acceptance(phase9_acceptance())
        frame = operator_evidence_frame(engine, identity, tactical, acceptance)
        self.assertEqual(engine.state.digest(), local_before)
        self.assertEqual(engine.ledger, ledger_before)
        self.assertEqual(len(frame["external_projections"]), 3)
        self.assertFalse(frame["external_clock_aligned"])
        self.assertFalse(frame["external_identity_promoted"])
        self.assertEqual(frame["authority"], "read_only_not_agent_knowledge")
        frame["external_projections"][0]["entity_id"] = "tampered"
        self.assertEqual(identity["entity_id"], "fixture_archivist")

    def test_operator_frame_rejects_forged_or_duplicate_projection(self):
        engine = CausalEngine(fixture())
        identity = observe_ace_identity(ace_status(), ace_retrieval())
        fake = deepcopy(identity)
        fake["entity_id"] = "forged"
        with self.assertRaisesRegex(EvidenceError, "mutated"):
            operator_evidence_frame(engine, fake)
        with self.assertRaisesRegex(EvidenceError, "duplicate"):
            operator_evidence_frame(engine, identity, identity)
        forged_authority = deepcopy(identity)
        forged_authority["authority"] = "source_canon"
        forged_authority["projection_sha256"] = canonical_sha256({
            k: v for k, v in forged_authority.items()
            if k != "projection_sha256"
        })
        with self.assertRaises(EvidenceError):
            operator_evidence_frame(engine, forged_authority)


if __name__ == "__main__":
    unittest.main()
