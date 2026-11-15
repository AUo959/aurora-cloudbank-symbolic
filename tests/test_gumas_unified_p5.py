"""P5 distributed-governance acceptance and safety regression tests."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
import unittest

from simulation.runtime.gumas_unified import CausalEngine, FeasibilityError
from simulation.runtime.gumas_unified.distributed_actions import (
    distributed_council_view, motion_fingerprint,
)
from simulation.runtime.gumas_unified.distributed_scenario import (
    distributed_fixture, run_distributed, run_late_ballot,
)
from simulation.runtime.gumas_unified.model import RemoteBallot
from simulation.runtime.gumas_unified.political_actions import (
    institution_view, prepare_relief_proposal,
)
from simulation.runtime.gumas_unified.political_scenario import run_p3
from simulation.runtime.gumas_unified.governance_scenario import run_p4
from simulation.runtime.gumas_unified.scenario import run_experiment


def prepared_engine(protocol="veto", *, expiry=28):
    engine = CausalEngine(distributed_fixture(protocol),
                          run_id=f"synthetic-p5-accept-{protocol}-{expiry}")
    proposal = prepare_relief_proposal(
        engine, institution_id="relief_council", proposer_id="governor",
        route_id="corridor_a", commodity="rations", amount=3,
        expires_s=expiry)
    motion_id = engine.propose_relief(
        proposal, cause="actor:governor-proposal").effect["motion_id"]
    return engine, motion_id


def delivered_notice(engine, motion_id):
    engine.send_policy_notice(
        motion_id, "governor", "member_b", "corridor_a",
        cause="actor:notice-over-corridor")
    engine.advance_to(4)


class P5DistributedGovernanceTests(unittest.TestCase):
    def test_veto_remote_yes_changes_resources_only_after_ballot_arrives(self):
        result = run_distributed("veto")
        self.assertEqual(result["before_ballot"]["institution"]["motions"][
            result["motion_id"]]["yes_votes"], 2)
        self.assertEqual(result["before_ballot"]["in_flight_ballot_counts"],
                         {result["motion_id"]: 1})
        self.assertEqual(result["counted_council"]["institution"]["motions"][
            result["motion_id"]]["yes_votes"], 3)
        self.assertEqual(result["counted_council"]["in_flight_ballot_counts"], {})
        self.assertEqual(result["at_20s"]["destination"]["inventory"]["rations"], 6)
        self.assertEqual(result["at_20s"]["origin"]["inventory"]["rations"], 17)
        self.assertTrue(result["evidence"]["ledger_valid"])
        self.assertEqual(result["evidence"]["resource_totals"],
                         {"energy_j": 110000, "rations": 23})

    def test_remote_veto_no_physically_prevents_allocation(self):
        result = run_distributed("veto", remote_approves=False)
        motion = result["counted_council"]["institution"]["motions"][
            result["motion_id"]]
        self.assertEqual(motion["status"], "rejected")
        self.assertEqual((motion["yes_votes"], motion["no_votes"]), (2, 1))
        self.assertEqual(result["at_20s"]["destination"]["inventory"]["rations"], 3)
        self.assertEqual(result["at_20s"]["origin"]["inventory"]["rations"], 20)
        self.assertTrue(result["evidence"]["ledger_valid"])

    def test_unanimous_distributed_members_all_required(self):
        result = run_distributed("unanimous")
        self.assertEqual(result["before_ballot"]["institution"]["motions"][
            result["motion_id"]]["yes_votes"], 2)
        self.assertEqual(result["counted_council"]["institution"]["motions"][
            result["motion_id"]]["yes_votes"], 3)
        self.assertEqual(result["at_20s"]["destination"]["inventory"]["rations"], 6)
        self.assertEqual(result["evidence"]["resource_totals"]["rations"], 23)

    def test_remote_delegate_can_decide_without_fabricated_local_vote(self):
        result = run_distributed("delegated")
        self.assertEqual(result["before_ballot"]["institution"]["motions"][
            result["motion_id"]]["yes_votes"], 0)
        self.assertEqual(result["counted_council"]["institution"]["motions"][
            result["motion_id"]]["yes_votes"], 1)
        self.assertEqual(result["at_20s"]["destination"]["inventory"]["rations"], 6)

    def test_remote_delegate_no_rejects_without_material_effect(self):
        result = run_distributed("delegated", remote_approves=False)
        self.assertEqual(result["counted_council"]["institution"]["motions"][
            result["motion_id"]]["status"], "rejected")
        self.assertEqual(result["at_20s"]["destination"]["inventory"]["rations"], 3)

    def test_delivered_notice_contains_actionable_public_motion_terms(self):
        engine, motion_id = prepared_engine()
        engine.send_policy_notice(
            motion_id, "governor", "member_b", "corridor_a",
            cause="actor:deliver-actionable-proposal")
        self.assertEqual(engine.actor_view("member_b")["received_reports"], [])
        engine.advance_to(4)
        notice = engine.actor_view("member_b")["received_reports"][0]
        terms = notice["proposal"]
        self.assertEqual(terms["motion_id"], motion_id)
        self.assertEqual(terms["commodity"], "rations")
        self.assertEqual(terms["amount"], 3)
        self.assertEqual(terms["route_id"], "corridor_a")
        self.assertEqual(terms["expires_s"], 28)
        self.assertEqual(notice["motion_sha256"],
                         motion_fingerprint(engine.state.relief_motions[motion_id]))

    def test_matching_fingerprint_without_correct_terms_cannot_support_ballot(self):
        engine, motion_id = prepared_engine()
        world = engine.state
        motion = world.relief_motions[motion_id]
        world.actors["member_b"].received_reports.append({
            "kind": "policy_motion_notice", "motion_id": motion_id,
            "institution_id": motion.institution_id,
            "motion_sha256": motion_fingerprint(motion),
            "proposal": {"amount": 999},
            "received_s": 0, "sent_s": 0,
        })
        forged = CausalEngine(world, run_id="synthetic-p5-fabricated-notice")
        before = forged.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "has not received"):
            forged.submit_remote_ballot(
                motion_id, "member_b", True, "return_signal",
                cause="actor:invalid-motion-content")
        self.assertEqual(forged.state.digest(), before)

    def test_notice_must_arrive_before_remote_actor_can_vote(self):
        engine, motion_id = prepared_engine()
        before, n = engine.state.digest(), len(engine.ledger)
        with self.assertRaisesRegex(FeasibilityError, "has not received"):
            engine.submit_remote_ballot(
                motion_id, "member_b", True, "return_signal",
                cause="actor:uninformed-vote")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(len(engine.ledger), n)
        engine.send_policy_notice(
            motion_id, "governor", "member_b", "corridor_a",
            cause="actor:notice")
        engine.advance_to(3)
        with self.assertRaisesRegex(FeasibilityError, "has not received"):
            engine.submit_remote_ballot(
                motion_id, "member_b", True, "return_signal",
                cause="actor:too-early")
        self.assertEqual(engine.actor_view("member_b")["received_reports"], [])
        engine.advance_to(4)
        self.assertEqual(len(engine.actor_view("member_b")["received_reports"]), 1)

    def test_notice_does_not_appear_early_in_recipient_private_view(self):
        result = run_distributed("veto")
        self.assertEqual(result["before_notice"]["received_reports"], [])
        received = result["after_notice"]["received_reports"]
        self.assertEqual(len(received), 1)
        notice = received[0]
        self.assertEqual(notice["kind"], "policy_motion_notice")
        self.assertEqual((notice["sent_s"], notice["received_s"]), (0, 4))
        self.assertEqual(notice["motion_id"], result["motion_id"])
        self.assertNotIn("ballot_intent_approve", notice)

    def test_return_signal_is_directed_and_has_separate_delay(self):
        result = run_distributed("veto")
        sent = result["remote_ballot_sent"]
        self.assertEqual(sent["route_id"], "return_signal")
        self.assertEqual((sent["sent_s"], sent["arrival_s"]), (4, 8))
        self.assertFalse(sent["counted_by_institution"])
        arrival = next(
            row for row in result["evidence"]["ledger"]
            if row["kind"] == "policy_ballot_arrival")
        self.assertEqual(arrival["time_s"], 8)
        self.assertTrue(arrival["effect"]["counted_by_institution"])
        self.assertEqual(arrival["effect"]["received_s"], 8)

    def test_in_transit_ballot_cannot_ratify_institution(self):
        engine, motion_id = prepared_engine("veto")
        engine.cast_relief_vote(
            motion_id, "governor", True, cause="actor:first")
        engine.cast_relief_vote(
            motion_id, "member_a", True, cause="actor:second")
        delivered_notice(engine, motion_id)
        engine.submit_remote_ballot(
            motion_id, "member_b", True, "return_signal",
            cause="actor:remote-vote")
        engine.advance_to(7)
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "approval"):
            engine.ratify_relief(motion_id, "governor",
                                cause="institution:try-to-count-inflight")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.state.relief_motions[motion_id].escrow_amount, 0)
        self.assertEqual(engine.site_view("union_depot")["inventory"]["rations"], 20)

    def test_ballot_after_expiration_is_recorded_but_not_counted(self):
        result = run_late_ballot()
        self.assertEqual(result["at_expiry"]["motions"][
            next(iter(result["at_expiry"]["motions"]))]["status"], "expired")
        motion = next(iter(result["after_arrival"]["motions"].values()))
        self.assertEqual(motion["yes_votes"], 2)
        self.assertEqual(motion["status"], "expired")
        self.assertEqual(result["final_ballot_status"], "arrived_unusable")
        receipt = next(row for row in result["evidence"]["ledger"]
                       if row["kind"] == "policy_ballot_arrival")
        self.assertFalse(receipt["effect"]["counted_by_institution"])
        self.assertEqual(receipt["effect"]["delivery_outcome"],
                         "expired_or_closed_motion")
        self.assertTrue(result["evidence"]["ledger_valid"])

    def test_ballot_at_exact_expiry_is_not_counted(self):
        engine, motion_id = prepared_engine("veto", expiry=8)
        delivered_notice(engine, motion_id)
        engine.submit_remote_ballot(
            motion_id, "member_b", True, "return_signal",
            cause="actor:exact-deadline")
        engine.advance_to(8)
        self.assertEqual(engine.state.relief_motions[motion_id].status, "expired")
        self.assertEqual(engine.state.relief_motions[motion_id].votes, {})
        self.assertEqual(next(iter(engine.state.remote_ballots.values())).status,
                         "arrived_unusable")

    def test_duplicate_inflight_ballot_fails_atomically(self):
        engine, motion_id = prepared_engine()
        delivered_notice(engine, motion_id)
        engine.submit_remote_ballot(
            motion_id, "member_b", True, "return_signal",
            cause="actor:first-choice")
        before, ledger = engine.state.digest(), engine.ledger
        with self.assertRaisesRegex(FeasibilityError, "duplicate"):
            engine.submit_remote_ballot(
                motion_id, "member_b", False, "return_signal",
                cause="actor:double-choice")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.ledger, ledger)

    def test_duplicate_delivered_ballot_fails(self):
        engine, motion_id = prepared_engine()
        delivered_notice(engine, motion_id)
        engine.submit_remote_ballot(
            motion_id, "member_b", True, "return_signal",
            cause="actor:first-choice")
        engine.advance_to(8)
        with self.assertRaisesRegex(FeasibilityError, "duplicate"):
            engine.submit_remote_ballot(
                motion_id, "member_b", False, "return_signal",
                cause="actor:duplicate-late")

    def test_remote_actor_cannot_use_direct_local_vote(self):
        engine, motion_id = prepared_engine()
        with self.assertRaisesRegex(FeasibilityError, "local presence"):
            engine.cast_relief_vote(
                motion_id, "member_b", True,
                cause="actor:skipping-transmission")

    def test_reverse_route_must_exist_explicitly(self):
        engine, motion_id = prepared_engine()
        delivered_notice(engine, motion_id)
        before = engine.state.digest()
        with self.assertRaises(FeasibilityError):
            engine.submit_remote_ballot(
                motion_id, "member_b", True, "corridor_a",
                cause="actor:wrong-direction")
        with self.assertRaises(FeasibilityError):
            engine.submit_remote_ballot(
                motion_id, "member_b", True, "nonexistent",
                cause="actor:no-return-path")
        self.assertEqual(engine.state.digest(), before)

    def test_no_signal_power_at_remote_origin_fails_atomically(self):
        world = distributed_fixture("veto")
        world.sites["frontier_port"].inventory["energy_j"] = 0
        engine = CausalEngine(world)
        proposal = prepare_relief_proposal(
            engine, institution_id="relief_council", proposer_id="governor",
            route_id="corridor_a", commodity="rations", amount=3,
            expires_s=28)
        motion_id = engine.propose_relief(proposal, cause="actor:propose").effect["motion_id"]
        delivered_notice(engine, motion_id)
        before, ledger = engine.state.digest(), engine.ledger
        with self.assertRaisesRegex(FeasibilityError, "energy"):
            engine.submit_remote_ballot(
                motion_id, "member_b", True, "return_signal",
                cause="actor:unpowered")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.ledger, ledger)

    def test_no_signal_power_at_seat_refuses_notice(self):
        world = distributed_fixture("veto")
        world.sites["union_depot"].inventory["energy_j"] = 0
        engine = CausalEngine(world)
        proposal = prepare_relief_proposal(
            engine, institution_id="relief_council", proposer_id="governor",
            route_id="corridor_a", commodity="rations", amount=3,
            expires_s=28)
        motion_id = engine.propose_relief(proposal, cause="actor:propose").effect["motion_id"]
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "energy"):
            engine.send_policy_notice(
                motion_id, "governor", "member_b", "corridor_a",
                cause="actor:unpowered-notice")
        self.assertEqual(engine.state.digest(), before)

    def test_non_member_cannot_receive_authorized_motion_notice(self):
        engine, motion_id = prepared_engine()
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "known members"):
            engine.send_policy_notice(
                motion_id, "governor", "observer", "corridor_a",
                cause="actor:outside-council")
        self.assertEqual(engine.state.digest(), before)

    def test_local_actor_cannot_submit_remote_ballot(self):
        engine, motion_id = prepared_engine()
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "seat-local"):
            engine.submit_remote_ballot(
                motion_id, "governor", True, "corridor_a",
                cause="actor:wrong-channel")
        self.assertEqual(engine.state.digest(), before)

    def test_remote_voter_under_delegated_rule_must_be_delegate(self):
        engine, motion_id = prepared_engine("delegated")
        delivered_notice(engine, motion_id)
        state = engine.state
        self.assertEqual(state.governance_rules["relief_council"].delegate_id,
                         "member_b")
        engine.submit_remote_ballot(
            motion_id, "member_b", True, "return_signal",
            cause="actor:delegate-choice")
        engine.advance_to(8)
        self.assertTrue(engine.state.relief_motions[motion_id].votes["member_b"])

    def test_unauthorized_notices_and_repeat_notices_fail(self):
        engine, motion_id = prepared_engine()
        with self.assertRaisesRegex(FeasibilityError, "known members"):
            engine.send_policy_notice(
                motion_id, "local_dissenter", "member_b", "corridor_a",
                cause="actor:nonmember-notice")
        engine.send_policy_notice(
            motion_id, "governor", "member_b", "corridor_a",
            cause="actor:first-notice")
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "already"):
            engine.send_policy_notice(
                motion_id, "governor", "member_b", "corridor_a",
                cause="actor:repeat-notice")
        self.assertEqual(engine.state.digest(), before)
        engine.advance_to(4)
        with self.assertRaisesRegex(FeasibilityError, "already"):
            engine.send_policy_notice(
                motion_id, "governor", "member_b", "corridor_a",
                cause="actor:repeat-delivered")

    def test_no_original_p4_or_p3_observation_change_without_p5_state(self):
        for mode in ("delegated", "unanimous", "veto"):
            result = run_p4(mode)
            self.assertTrue(result["evidence"]["ledger_valid"])
            self.assertEqual(result["destination"]["inventory"]["rations"], 6)
        p3 = run_p3()
        self.assertTrue(p3["evidence"]["ledger_valid"])
        self.assertEqual(p3["arrival"]["destination"]["inventory"]["rations"], 6)
        self.assertEqual(run_experiment()["evidence"]["final_state"],
                         "518eff3927c3f38d7c6e8faa46c011d7f411ce410357cf6b92f83abcb3e1e11c")

    def test_empty_p5_state_keeps_the_original_p4_state_digest(self):
        world = distributed_fixture("veto")
        payload = asdict(world)
        self.assertEqual(payload.pop("remote_ballots"), {})
        for optional in ("identity_bindings", "relief_motions"):
            if not payload[optional]:
                payload.pop(optional)
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.assertEqual(world.digest(), hashlib.sha256(encoded).hexdigest())

    def test_cross_polity_membership_and_local_assembly_are_independent(self):
        world = distributed_fixture("veto")
        self.assertEqual(world.actors["member_b"].site_id, "frontier_port")
        self.assertNotEqual(world.institutions["relief_council"].polity_id,
                            world.institutions["frontier_assembly"].polity_id)
        self.assertIn("member_b", world.institutions["relief_council"].members)
        self.assertIn("member_b", world.institutions["frontier_assembly"].members)
        engine = CausalEngine(world)
        proposal = prepare_relief_proposal(
            engine, institution_id="frontier_assembly", proposer_id="member_b",
            route_id="return_signal", commodity="rations", amount=1,
            expires_s=30)
        motion_id = engine.propose_relief(
            proposal, cause="actor:independent-frontier-assembly").effect["motion_id"]
        self.assertEqual(engine.state.relief_motions[motion_id].institution_id,
                         "frontier_assembly")
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_distributed_outcome_is_independent_of_polity_names(self):
        world = distributed_fixture("veto")
        world.sites["union_depot"].polity_id = "fictional_polity_gamma"
        world.sites["frontier_port"].polity_id = "fictional_polity_delta"
        world.institutions["relief_council"].polity_id = "fictional_polity_gamma"
        world.institutions["frontier_assembly"].polity_id = "fictional_polity_delta"
        engine = CausalEngine(world)
        proposal = prepare_relief_proposal(
            engine, institution_id="relief_council", proposer_id="governor",
            route_id="corridor_a", commodity="rations", amount=3,
            expires_s=28)
        motion_id = engine.propose_relief(
            proposal, cause="actor:local-proposal").effect["motion_id"]
        engine.cast_relief_vote(motion_id, "governor", True, cause="actor:yes")
        engine.cast_relief_vote(motion_id, "member_a", True, cause="actor:yes")
        delivered_notice(engine, motion_id)
        engine.submit_remote_ballot(
            motion_id, "member_b", True, "return_signal", cause="actor:remote-yes")
        engine.advance_to(8)
        engine.ratify_relief(motion_id, "governor", cause="institution:consent")
        engine.dispatch_ratified_relief(motion_id, "governor", cause="actor:physical")
        engine.advance_to(20)
        self.assertEqual(engine.site_view("frontier_port")["inventory"]["rations"], 6)
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_remote_vote_is_atomic_against_invalid_boolean(self):
        engine, motion_id = prepared_engine()
        delivered_notice(engine, motion_id)
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "yes or no"):
            engine.submit_remote_ballot(
                motion_id, "member_b", 1, "return_signal", cause="actor:integer-yes")
        self.assertEqual(engine.state.digest(), before)

    def test_p2_identity_reference_is_provenance_not_voting_authority(self):
        from simulation.runtime.gumas_unified.external_evidence import observe_ace_identity

        engine, motion_id = prepared_engine("veto")
        source = {
            "world_id": "p5-fixture-world",
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
            "world_id": source["world_id"],
            "world_scope": "isolated_aurora_world",
            "request_id": "synthetic-p5-id-retrieval",
            "operation": "retrieve",
            "status": "RETRIEVED_CANON",
            "determination_id": "synthetic-p5-determination",
            "entity_id": "fixture_remote_actor",
            "character": {
                "canonical_id": "fixture_remote_actor",
                "name": "Fixture Remote Participant",
            },
            "origin": "sandbox_created",
        }
        ace = observe_ace_identity(source, response)
        state = engine.state
        grant = {
            "schema": "gumas.unified.fixture_binding_grant.p2",
            "operation": "bind_fixture_identity",
            "scope": "synthetic_fixture_only",
            "grant_ref": "fixture:p5-actor-alias",
            "operator_intent_explicit": True,
            "run_id": engine.run_id, "state_sha256": state.digest(),
            "actor_id": "member_b", "site_id": "frontier_port",
            "world_id": ace["world_id"], "entity_id": ace["entity_id"],
            "ace_projection_sha256": ace["projection_sha256"],
            "effective_at_s": state.time_s, "valid_until_s": 28,
            "allow_canon_promotion": False,
            "allow_agent_memory_injection": False,
            "allow_permission_changes": False,
        }
        engine.bind_fixture_identity(ace, grant)
        binding = engine.state.identity_bindings["member_b"]
        delivered_notice(engine, motion_id)
        receipt = engine.submit_remote_ballot(
            motion_id, "member_b", True, "return_signal",
            cause="actor:p5-bound-member-votes")
        self.assertEqual(receipt.effect["voter_binding_sha256"],
                         binding["binding_sha256"])
        self.assertFalse(binding["source_canon_promoted"])
        self.assertFalse(binding["actor_permissions_changed"])
        self.assertFalse(binding["agent_memory_injected"])
        self.assertEqual(engine.state.relief_motions[motion_id].votes, {})
        engine.advance_to(8)
        self.assertTrue(engine.state.relief_motions[motion_id].votes["member_b"])
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_directly_injected_unproven_remote_ballot_fails_state_validation(self):
        world = distributed_fixture("veto")
        world.remote_ballots["fake"] = RemoteBallot(
            "fake", "absent_motion", "member_b", "return_signal",
            True, 0, 4, "f" * 64)
        with self.assertRaisesRegex(ValueError, "missing motion"):
            CausalEngine(world)

    def test_remote_ballot_cannot_create_auto_ratification(self):
        result = run_distributed("veto")
        kinds = [entry["kind"] for entry in result["evidence"]["ledger"]]
        self.assertLess(kinds.index("policy_notice_sent"),
                        kinds.index("policy_notice_arrival"))
        self.assertLess(kinds.index("policy_notice_arrival"),
                        kinds.index("remote_ballot_sent"))
        self.assertLess(kinds.index("remote_ballot_sent"),
                        kinds.index("policy_ballot_arrival"))
        self.assertLess(kinds.index("policy_ballot_arrival"),
                        kinds.index("relief_ratified_and_reserved"))
        self.assertLess(kinds.index("relief_ratified_and_reserved"),
                        kinds.index("relief_shipment_departed"))
        self.assertLess(kinds.index("relief_shipment_departed"),
                        kinds.index("cargo_arrival"))

    def test_synthetic_context_is_non_authoritative_and_deterministic(self):
        result = run_distributed("veto")
        self.assertEqual(result, run_distributed("veto"))
        self.assertEqual(result["authority"], "synthetic_L2_only")
        self.assertFalse(result["remote_ballot_sent"]["counted_by_institution"])
        self.assertFalse(result["before_ballot"][
            "pending_ballot_choices_visible_to_institution"])
        self.assertEqual(result["observer_before_report"]["received_reports"], [])
        self.assertEqual(len(result["observer_after_report"]["received_reports"]), 1)
        self.assertTrue(result["evidence"]["ledger_valid"])

    def test_signals_consume_energy_but_do_not_destroy_it(self):
        result = run_distributed("veto")
        events = result["evidence"]["ledger"]
        signals = [entry for entry in events
                   if entry["kind"] in ("policy_notice_sent", "remote_ballot_sent",
                                        "report_sent")]
        self.assertEqual(len(signals), 3)
        self.assertTrue(all(entry["effect"]["energy_to_heat_j"] == 1200
                            for entry in signals))
        self.assertEqual(result["evidence"]["resource_totals"]["energy_j"], 110000)
        self.assertEqual(result["evidence"]["resource_totals"]["rations"], 23)


if __name__ == "__main__":
    unittest.main()
