"""P4 contract tests: heterogeneous governance rules, shared physical consequences."""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import unittest

from simulation.runtime.gumas_unified import CausalEngine, FeasibilityError
from simulation.runtime.gumas_unified.governance_scenario import (
    governance_fixture, run_p4,
)
from simulation.runtime.gumas_unified.model import GovernanceProtocol, Institution
from simulation.runtime.gumas_unified.political_actions import (
    institution_view, prepare_relief_proposal,
)
from simulation.runtime.gumas_unified.political_scenario import p3_fixture, run_p3
from simulation.runtime.gumas_unified.scenario import run_experiment


def start(protocol: str):
    engine = CausalEngine(governance_fixture(protocol),
                          run_id=f"synthetic-p4-test-{protocol}")
    proposal = prepare_relief_proposal(
        engine, institution_id="relief_council", proposer_id="governor",
        route_id="corridor_a", commodity="rations", amount=3, expires_s=30)
    motion_id = engine.propose_relief(
        proposal, cause="actor:policy-proposal").effect["motion_id"]
    return engine, motion_id


def vote(engine, motion_id, actor, answer=True):
    return engine.cast_relief_vote(
        motion_id, actor, answer, cause=f"actor:{actor}-ballot")


def ratify_and_dispatch(engine, motion_id):
    engine.ratify_relief(
        motion_id, "governor", cause="institution:authority-recorded")
    return engine.dispatch_ratified_relief(
        motion_id, "governor", cause="actor:execute-policy")


class P4GovernanceTests(unittest.TestCase):
    def test_three_protocols_converge_on_same_conserved_material_effect(self):
        for protocol in ("delegated", "unanimous", "veto"):
            with self.subTest(protocol=protocol):
                result = run_p4(protocol)
                self.assertTrue(result["evidence"]["ledger_valid"])
                self.assertEqual(result["destination"]["inventory"]["rations"], 6)
                self.assertEqual(result["local"]["inventory"]["rations"], 17)
                self.assertEqual(result["source_polity"]["available"]["rations"], 17)
                self.assertEqual(result["evidence"]["resource_totals"],
                                 {"energy_j": 110000, "rations": 23})
                self.assertEqual(result["after"]["decision_protocol"], protocol)

    def test_protocol_requires_different_numbers_of_actual_actor_votes(self):
        counts = {p: len([e for e in run_p4(p)["evidence"]["ledger"]
                          if e["kind"] == "relief_vote_recorded"])
                  for p in ("delegated", "unanimous", "veto")}
        self.assertEqual(counts, {"delegated": 1, "unanimous": 3, "veto": 3})

    def test_delegated_vote_is_authority_not_general_member_ballot(self):
        engine, motion_id = start("delegated")
        before, n = engine.state.digest(), len(engine.ledger)
        with self.assertRaisesRegex(FeasibilityError, "eligible"):
            vote(engine, motion_id, "member_a")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(len(engine.ledger), n)
        receipt = vote(engine, motion_id, "governor", True)
        self.assertEqual(receipt.effect["decision_protocol"], "delegated")
        dispatched = ratify_and_dispatch(engine, motion_id)
        self.assertTrue(dispatched.effect["institutionally_authorized"])

    def test_delegation_refusal_blocks_ratification(self):
        engine, motion_id = start("delegated")
        no = vote(engine, motion_id, "governor", False)
        self.assertEqual(no.effect["status"], "rejected")
        before = engine.state.digest()
        with self.assertRaises(FeasibilityError):
            engine.ratify_relief(motion_id, "governor", cause="actor:wrong")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.site_view("union_depot")["inventory"]["rations"], 20)

    def test_unanimity_rejects_negative_ballot_immediately(self):
        engine, motion_id = start("unanimous")
        vote(engine, motion_id, "governor", True)
        no = vote(engine, motion_id, "member_b", False)
        self.assertEqual(no.effect["status"], "rejected")
        with self.assertRaises(FeasibilityError):
            vote(engine, motion_id, "member_a")
        self.assertEqual(engine.state.totals()["rations"], 23)

    def test_unanimity_waits_for_all_members_without_inventing_votes(self):
        engine, motion_id = start("unanimous")
        vote(engine, motion_id, "governor", True)
        vote(engine, motion_id, "member_a", True)
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "quorum"):
            engine.ratify_relief(motion_id, "governor",
                                cause="institution:missing-participant")
        self.assertEqual(before, engine.state.digest())
        vote(engine, motion_id, "member_b", True)
        self.assertEqual(ratify_and_dispatch(engine, motion_id).kind,
                         "relief_shipment_departed")

    def test_veto_holder_is_essential_even_when_quorum_met(self):
        engine, motion_id = start("veto")
        vote(engine, motion_id, "governor", True)
        vote(engine, motion_id, "member_a", True)
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "governance"):
            engine.ratify_relief(motion_id, "governor",
                                cause="institution:no-veto-holder-assent")
        self.assertEqual(engine.state.digest(), before)
        vote(engine, motion_id, "member_b", True)
        ratify_and_dispatch(engine, motion_id)
        self.assertEqual(engine.state.totals()["rations"], 23)

    def test_negative_veto_prevents_resource_transfer(self):
        result = run_p4("veto", veto_yes=False)
        self.assertEqual(result["destination"]["inventory"]["rations"], 3)
        self.assertEqual(result["local"]["inventory"]["rations"], 20)
        self.assertEqual(result["after"]["motions"][
            next(iter(result["after"]["motions"]))]["status"], "rejected")
        self.assertEqual(result["evidence"]["resource_totals"]["rations"], 23)
        self.assertTrue(result["evidence"]["ledger_valid"])

    def test_veto_holder_can_vote_first_and_force_rejection(self):
        engine, motion_id = start("veto")
        receipt = vote(engine, motion_id, "member_b", False)
        self.assertEqual(receipt.effect["status"], "rejected")
        self.assertEqual(len(engine.state.relief_motions[motion_id].votes), 1)
        with self.assertRaises(FeasibilityError):
            vote(engine, motion_id, "governor", True)

    def test_existing_p3_ledger_and_data_are_identical_without_p4_override(self):
        # The P3 fixture has no governance_rules. Empty P4 fields must never
        # alter recorded P3 events, initial/final hashes or projection shapes.
        old = run_p3(council_choice="approve")
        self.assertTrue(old["evidence"]["ledger_valid"])
        self.assertNotIn("decision_protocol", old["reservation"]["institution"])
        for row in old["evidence"]["ledger"]:
            self.assertNotIn("decision_protocol", row["effect"])
        self.assertEqual(run_experiment()["evidence"]["final_state"],
                         "518eff3927c3f38d7c6e8faa46c011d7f411ce410357cf6b92f83abcb3e1e11c")
        world = p3_fixture()
        payload = asdict(world)
        self.assertEqual(payload.pop("governance_rules"), {})
        for field in ("identity_bindings", "relief_motions"):
            if not payload[field]:
                payload.pop(field)
        data = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.assertEqual(world.digest(), hashlib.sha256(data).hexdigest())

    def test_legacy_ballots_still_accept_quorum_without_unanimity(self):
        outcome = run_p3(council_choice="approve")
        motion = next(iter(outcome["ballots"]["motions"].values()))
        self.assertEqual(motion["yes_votes"], 2)
        self.assertEqual(outcome["arrival"]["destination"]["inventory"]["rations"], 6)

    def test_name_independence_with_different_polity_label(self):
        world = governance_fixture("veto")
        world.sites["union_depot"].polity_id = "fixture_other_polity"
        world.institutions["relief_council"].polity_id = "fixture_other_polity"
        engine = CausalEngine(world)
        proposal = prepare_relief_proposal(
            engine, institution_id="relief_council", proposer_id="governor",
            route_id="corridor_a", commodity="rations", amount=3, expires_s=30)
        motion_id = engine.propose_relief(proposal, cause="actor:decision").effect["motion_id"]
        for actor in ("governor", "member_a", "member_b"):
            vote(engine, motion_id, actor)
        ratify_and_dispatch(engine, motion_id)
        self.assertEqual(engine.polity_view("fixture_other_polity")
                         ["available"]["rations"], 17)

    def test_missing_governance_contract_uses_original_quorum(self):
        world = p3_fixture()
        self.assertEqual(world.governance_rules, {})
        engine = CausalEngine(world)
        self.assertNotIn("decision_protocol", institution_view(
            engine, "relief_council"))
        proposal = prepare_relief_proposal(
            engine, institution_id="relief_council", proposer_id="governor",
            route_id="corridor_a", commodity="rations", amount=3, expires_s=30)
        motion_id = engine.propose_relief(proposal, cause="actor:propose").effect["motion_id"]
        vote(engine, motion_id, "governor")
        vote(engine, motion_id, "member_a")
        ratify_and_dispatch(engine, motion_id)
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_rule_beyond_membership_is_rejected_at_initialization(self):
        world = governance_fixture("delegated")
        world.governance_rules["relief_council"] = GovernanceProtocol(
            "relief_council", "delegated", delegate_id="unknown_actor")
        with self.assertRaisesRegex(ValueError, "delegation"):
            CausalEngine(world)

    def test_veto_member_not_in_institution_is_invalid(self):
        world = governance_fixture("veto")
        world.governance_rules["relief_council"] = GovernanceProtocol(
            "relief_council", "veto", veto_ids=("foreign_actor",))
        with self.assertRaisesRegex(ValueError, "veto holders"):
            CausalEngine(world)

    def test_invalid_unanimity_threshold_fails_before_execution(self):
        world = governance_fixture("unanimous")
        world.institutions["relief_council"] = Institution(
            "relief_council", "union_depot",
            ("governor", "member_a", "member_b"), quorum=2,
            approval_threshold=2, polity_id="fixture_union")
        with self.assertRaisesRegex(ValueError, "unanimous"):
            CausalEngine(world)

    def test_unrecognized_governance_mode_fails_closed(self):
        world = governance_fixture("veto")
        world.governance_rules["relief_council"] = GovernanceProtocol(
            "relief_council", "imperium_preferred", veto_ids=("member_b",))
        with self.assertRaisesRegex(ValueError, "unknown"):
            CausalEngine(world)

    def test_duplicate_veto_holders_are_rejected(self):
        world = governance_fixture("veto")
        world.governance_rules["relief_council"] = GovernanceProtocol(
            "relief_council", "veto", veto_ids=("member_b", "member_b"))
        with self.assertRaisesRegex(ValueError, "veto holders"):
            CausalEngine(world)

    def test_attempt_to_vote_from_remote_site_rejected(self):
        world = governance_fixture("unanimous")
        world.actors["member_b"].site_id = "frontier_port"
        engine = CausalEngine(world)
        proposal = prepare_relief_proposal(
            engine, institution_id="relief_council", proposer_id="governor",
            route_id="corridor_a", commodity="rations", amount=3, expires_s=30)
        motion_id = engine.propose_relief(proposal, cause="actor:propose").effect["motion_id"]
        with self.assertRaisesRegex(FeasibilityError, "local presence"):
            vote(engine, motion_id, "member_b", True)
        self.assertEqual(engine.state.relief_motions[motion_id].votes, {})

    def test_tactical_and_ace_remain_externally_uninvoked(self):
        result = run_p4("veto")
        self.assertEqual(result["status"], "L2_synthetic_noncanonical")
        self.assertFalse(any("tactical" in event["kind"]
                             for event in result["evidence"]["ledger"]))
        self.assertFalse(any("canon" in event["kind"]
                             for event in result["evidence"]["ledger"]))
        self.assertEqual(result["observer_before_signal"]["received_reports"], [])
        self.assertEqual(len(result["observer_after_signal"]["received_reports"]), 1)

    def test_deterministic_replay_and_refusal_of_duplicate_dispatch(self):
        for mode in ("delegated", "unanimous", "veto"):
            initial = run_p4(mode)
            replay = run_p4(mode)
            self.assertEqual(initial, replay)
        engine, motion_id = start("delegated")
        vote(engine, motion_id, "governor")
        ratify_and_dispatch(engine, motion_id)
        before = engine.state.digest()
        with self.assertRaises(FeasibilityError):
            engine.dispatch_ratified_relief(
                motion_id, "governor", cause="actor:duplicate")
        self.assertEqual(engine.state.digest(), before)

    def test_financial_resources_reconcile_across_all_protocols(self):
        for mode in ("delegated", "unanimous", "veto"):
            output = run_p4(mode)
            self.assertEqual(output["evidence"]["resource_totals"]["energy_j"], 110000)
            self.assertEqual(output["evidence"]["resource_totals"]["rations"], 23)
            self.assertEqual(output["recipient_polity"]["available"]["rations"], 6)
            self.assertEqual(output["source_polity"]["available"]["rations"], 17)

    def test_governance_rule_snapshot_does_not_mutate_committed_state(self):
        engine = CausalEngine(governance_fixture("veto"))
        before = engine.state.digest()
        snapshot = engine.state
        snapshot.governance_rules["relief_council"] = GovernanceProtocol(
            "relief_council", "delegated", delegate_id="governor")
        self.assertEqual(before, engine.state.digest())
        self.assertEqual(engine.state.governance_rules["relief_council"].kind,
                         "veto")


if __name__ == "__main__":
    unittest.main()
