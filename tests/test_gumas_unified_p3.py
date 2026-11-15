"""P3 causal policy tests: agent decisions -> institutional vote -> material effects."""
from __future__ import annotations

from dataclasses import replace
import unittest

from simulation.runtime.gumas_unified import CausalEngine, FeasibilityError
from simulation.runtime.gumas_unified.model import Institution
from simulation.runtime.gumas_unified.political_actions import (
    institution_view, prepare_relief_proposal,
)
from simulation.runtime.gumas_unified.political_scenario import p3_fixture, run_p3


class PoliticalCausalTests(unittest.TestCase):
    def make_engine(self, *, amount=3, expire=30, world=None):
        engine = CausalEngine(world or p3_fixture(), run_id="synthetic-p3-test")
        proposal = prepare_relief_proposal(
            engine, institution_id="relief_council", proposer_id="governor",
            route_id="corridor_a", commodity="rations",
            amount=amount, expires_s=expire)
        motion_id = engine.propose_relief(
            proposal, cause="actor:governor-proposes").effect["motion_id"]
        return engine, motion_id

    @staticmethod
    def approve(engine, motion_id):
        engine.cast_relief_vote(motion_id, "governor", True,
                                cause="actor:governor-yes")
        engine.cast_relief_vote(motion_id, "member_a", True,
                                cause="actor:member-a-yes")
        return engine.ratify_relief(
            motion_id, "governor", cause="institution:quorum-met")

    def test_yes_scenario_actor_institution_physics_macro(self):
        outcome = run_p3()
        self.assertEqual(outcome["scope"], "synthetic_L2_only")
        self.assertTrue(outcome["evidence"]["ledger_valid"])
        self.assertEqual(outcome["ballots"]["motions"][next(iter(
            outcome["ballots"]["motions"]))]["yes_votes"], 2)
        self.assertEqual(outcome["reservation"]["origin"]["inventory"]["rations"], 17)
        self.assertEqual(outcome["reservation"]["origin"]["reserved"], {"rations": 3})
        self.assertEqual(outcome["reservation"]["union"]["reserved"], {"rations": 3})
        self.assertEqual(outcome["departure"]["frontier"]["available"]["rations"], 3)
        self.assertEqual(outcome["departure"]["frontier"]["incoming"]["rations"], 3)
        self.assertEqual(outcome["arrival"]["destination"]["inventory"]["rations"], 6)
        self.assertEqual(outcome["evidence"]["resource_totals"],
                         {"rations": 23, "energy_j": 110000})

    def test_negative_ballots_change_political_and_material_outcomes(self):
        approved, rejected = run_p3(council_choice="approve"), run_p3(
            council_choice="reject")
        self.assertIsNone(rejected["reservation"])
        self.assertEqual(rejected["arrival"]["destination"]["inventory"]["rations"], 3)
        self.assertEqual(rejected["arrival"]["origin"]["inventory"]["rations"], 20)
        self.assertEqual(approved["arrival"]["destination"]["inventory"]["rations"], 6)
        self.assertNotEqual(approved["evidence"]["final_state"],
                            rejected["evidence"]["final_state"])
        motion = next(iter(rejected["arrival"]["institution"]["motions"].values()))
        self.assertEqual(motion["status"], "rejected")
        self.assertEqual(motion["no_votes"], 2)
        self.assertEqual(approved["evidence"]["resource_totals"],
                         rejected["evidence"]["resource_totals"])

    def test_information_arrives_only_after_route_delay(self):
        for choice in ("approve", "reject"):
            outcome = run_p3(council_choice=choice)
            self.assertEqual(outcome["before_report"]["received_reports"], [])
            self.assertEqual(len(outcome["after_report"]["received_reports"]), 1)
            message = outcome["after_report"]["received_reports"][0]
            self.assertEqual((message["sent_s"], message["received_s"]), (0, 4))
            self.assertIn(choice, message["text"])
            self.assertEqual(outcome["departure"]["remote_observer"]
                             ["received_reports"], [])

    def test_p2_binding_provenance_and_no_private_background(self):
        outcome = run_p3()
        events = outcome["evidence"]["ledger"]
        binding = outcome["binding"]["binding_sha256"]
        proposed = next(e for e in events if e["kind"] == "relief_proposed")
        governor_vote = next(e for e in events
                             if e["kind"] == "relief_vote_recorded"
                             and e["actor_id"] == "governor")
        self.assertEqual(proposed["effect"]["proposer_binding_sha256"], binding)
        self.assertEqual(governor_vote["effect"]["voter_binding_sha256"], binding)
        self.assertTrue(outcome["binding"]["active_at_current_time"])
        self.assertNotIn("Synthetic private detail", str(events))
        self.assertNotIn("background", str(events))

    def test_deterministic_scenarios_and_event_ledger(self):
        self.assertEqual(run_p3(), run_p3())
        self.assertEqual(run_p3(council_choice="reject"),
                         run_p3(council_choice="reject"))
        kinds = [e["kind"] for e in run_p3()["evidence"]["ledger"]]
        self.assertLess(kinds.index("relief_proposed"),
                        kinds.index("relief_vote_recorded"))
        self.assertLess(kinds.index("relief_vote_recorded"),
                        kinds.index("relief_ratified_and_reserved"))
        self.assertLess(kinds.index("relief_ratified_and_reserved"),
                        kinds.index("relief_shipment_departed"))
        self.assertLess(kinds.index("relief_shipment_departed"),
                        kinds.index("cargo_arrival"))

    def test_proposal_is_pure_until_committed(self):
        engine = CausalEngine(p3_fixture())
        before = engine.state.digest()
        proposal = prepare_relief_proposal(
            engine, institution_id="relief_council", proposer_id="governor",
            route_id="corridor_a", commodity="rations", amount=3, expires_s=30)
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.ledger, [])
        self.assertEqual(proposal.amount, 3)

    def test_tampered_or_stale_proposal_fails_atomically(self):
        engine = CausalEngine(p3_fixture())
        proposal = prepare_relief_proposal(
            engine, institution_id="relief_council", proposer_id="governor",
            route_id="corridor_a", commodity="rations", amount=3, expires_s=30)
        changed = replace(proposal, amount=8)
        with self.assertRaisesRegex(FeasibilityError, "modified"):
            engine.propose_relief(changed, cause="actor:tampered")
        engine.advance_to(1)
        before, n = engine.state.digest(), len(engine.ledger)
        with self.assertRaisesRegex(FeasibilityError, "stale"):
            engine.propose_relief(proposal, cause="actor:stale")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(len(engine.ledger), n)

    def test_only_members_at_institution_seat_can_propose_or_vote(self):
        engine = CausalEngine(p3_fixture())
        with self.assertRaisesRegex(FeasibilityError, "membership"):
            prepare_relief_proposal(
                engine, institution_id="relief_council",
                proposer_id="local_dissenter", route_id="corridor_a",
                commodity="rations", amount=3, expires_s=30)
        engine, motion_id = self.make_engine()
        with self.assertRaises(FeasibilityError):
            engine.cast_relief_vote(motion_id, "observer", True,
                                    cause="actor:remote-vote")
        local_engine, motion_id = self.make_engine()
        with self.assertRaisesRegex(FeasibilityError, "membership"):
            local_engine.cast_relief_vote(
                motion_id, "local_dissenter", True, cause="actor:not-member")
        world = p3_fixture()
        world.actors["member_a"].site_id = "frontier_port"
        remote_engine, motion_id = self.make_engine(world=world)
        with self.assertRaisesRegex(FeasibilityError, "local presence"):
            remote_engine.cast_relief_vote(motion_id, "member_a", True,
                                           cause="actor:remote-member")
        self.assertTrue(remote_engine.evidence()["ledger_valid"])

    def test_votes_are_unique_and_boolean(self):
        engine, motion_id = self.make_engine()
        engine.cast_relief_vote(motion_id, "governor", True, cause="actor:yes")
        before, n = engine.state.digest(), len(engine.ledger)
        with self.assertRaisesRegex(FeasibilityError, "already voted"):
            engine.cast_relief_vote(motion_id, "governor", False,
                                    cause="actor:second-ballot")
        with self.assertRaisesRegex(FeasibilityError, "yes or no"):
            engine.cast_relief_vote(motion_id, "member_a", 1, cause="actor:int-vote")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(len(engine.ledger), n)

    def test_inadequate_quorum_cannot_ratify(self):
        engine, motion_id = self.make_engine()
        engine.cast_relief_vote(motion_id, "governor", True, cause="actor:yes")
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "quorum"):
            engine.ratify_relief(motion_id, "governor", cause="institution:premature")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.site_view("union_depot")["inventory"]["rations"], 20)

    def test_no_majority_rejects_and_preserves_stock(self):
        engine, motion_id = self.make_engine()
        engine.cast_relief_vote(motion_id, "governor", True, cause="actor:yes")
        engine.cast_relief_vote(motion_id, "member_a", False, cause="actor:no-1")
        engine.cast_relief_vote(motion_id, "member_b", False, cause="actor:no-2")
        self.assertEqual(institution_view(engine, "relief_council")
                         ["motions"][motion_id]["status"], "rejected")
        self.assertEqual(engine.state.totals()["rations"], 23)
        self.assertEqual(engine.site_view("union_depot")["inventory"]["rations"], 20)
        with self.assertRaises(FeasibilityError):
            engine.ratify_relief(motion_id, "governor", cause="institution:invalid")

    def test_reservation_does_not_duplicate_supplies(self):
        engine, motion_id = self.make_engine()
        self.approve(engine, motion_id)
        self.assertEqual(engine.site_view("union_depot")["inventory"]["rations"], 17)
        self.assertEqual(engine.site_view("union_depot")["reserved"]["rations"], 3)
        self.assertEqual(engine.state.totals()["rations"], 23)
        self.assertEqual(engine.polity_view("fixture_union")["available"]["rations"], 17)
        self.assertEqual(engine.polity_view("fixture_union")["reserved"]["rations"], 3)

    def test_direct_actor_cannot_double_spend_reserved_stock(self):
        world = p3_fixture()
        world.corridors["corridor_a"].capacity_units_per_window = 100
        engine, motion_id = self.make_engine(world=world)
        self.approve(engine, motion_id)
        with self.assertRaisesRegex(FeasibilityError, "unavailable"):
            engine.dispatch("local_dissenter", "corridor_a", "rations", 18,
                            cause="actor:tries-escrow-double-spend")
        self.assertEqual(engine.state.relief_motions[motion_id].escrow_amount, 3)
        self.assertEqual(engine.state.totals()["rations"], 23)

    def test_ratification_requires_available_resources(self):
        world = p3_fixture()
        world.sites["union_depot"].inventory["rations"] = 2
        engine, motion_id = self.make_engine(world=world)
        engine.cast_relief_vote(motion_id, "governor", True, cause="actor:yes")
        engine.cast_relief_vote(motion_id, "member_a", True, cause="actor:yes")
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "available resources"):
            engine.ratify_relief(motion_id, "governor", cause="institution:no-stock")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.state.totals()["rations"], 5)

    def test_transport_checks_energy_and_capacity_without_escrow_loss(self):
        world = p3_fixture()
        world.sites["union_depot"].inventory["energy_j"] = 1
        engine, motion_id = self.make_engine(world=world)
        self.approve(engine, motion_id)
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "energy"):
            engine.dispatch_ratified_relief(
                motion_id, "governor", cause="actor:no-energy")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.state.relief_motions[motion_id].escrow_amount, 3)

        engine, motion_id = self.make_engine()
        self.approve(engine, motion_id)
        engine.disrupt_route("corridor_a", 2, cause="fixture:capacity-lost")
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "capacity"):
            engine.dispatch_ratified_relief(
                motion_id, "governor", cause="actor:no-capacity")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.state.relief_motions[motion_id].escrow_amount, 3)

    def test_policy_and_manual_dispatch_share_transport_capacity(self):
        engine, motion_id = self.make_engine()
        self.approve(engine, motion_id)
        engine.dispatch("local_dissenter", "corridor_a", "rations", 2,
                        cause="actor:unrelated-shipment")
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "capacity"):
            engine.dispatch_ratified_relief(
                motion_id, "governor", cause="actor:overdraw-route")
        self.assertEqual(engine.state.digest(), before)

    def test_institutional_violation_is_recorded_not_retroactively_forbidden(self):
        engine, motion_id = self.make_engine()
        self.approve(engine, motion_id)
        receipt = engine.dispatch_ratified_relief(
            motion_id, "local_dissenter", cause="actor:unauthorized-executor")
        self.assertFalse(receipt.effect["institutionally_authorized"])
        self.assertEqual(engine.state.relief_motions[motion_id].status, "dispatched")
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_no_duplicate_motion_fulfillment(self):
        engine, motion_id = self.make_engine()
        self.approve(engine, motion_id)
        engine.dispatch_ratified_relief(
            motion_id, "governor", cause="actor:fulfill-once")
        before = engine.state.digest()
        with self.assertRaises(FeasibilityError):
            engine.dispatch_ratified_relief(
                motion_id, "governor", cause="actor:fulfill-twice")
        self.assertEqual(engine.state.digest(), before)

    def test_policy_expiry_releases_undelivered_reserved_stock(self):
        engine, motion_id = self.make_engine(expire=2)
        self.approve(engine, motion_id)
        self.assertEqual(engine.state.relief_motions[motion_id].escrow_amount, 3)
        engine.advance_to(2)
        self.assertEqual(engine.state.relief_motions[motion_id].status, "expired")
        self.assertEqual(engine.site_view("union_depot")["inventory"]["rations"], 20)
        self.assertEqual(engine.state.totals()["rations"], 23)
        self.assertEqual(engine.ledger[-1].kind, "policy_expiry")
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_policy_expiry_rejects_new_votes(self):
        engine, motion_id = self.make_engine(expire=2)
        engine.advance_to(2)
        self.assertEqual(engine.state.relief_motions[motion_id].status, "expired")
        with self.assertRaises(FeasibilityError):
            engine.cast_relief_vote(motion_id, "governor", True,
                                    cause="actor:late-vote")

    def test_dispatch_moved_stock_stays_moved_after_expiry(self):
        engine, motion_id = self.make_engine(expire=20)
        self.approve(engine, motion_id)
        engine.dispatch_ratified_relief(motion_id, "governor", cause="actor:ship")
        engine.advance_to(20)
        self.assertEqual(engine.state.relief_motions[motion_id].status, "dispatched")
        self.assertEqual(engine.site_view("union_depot")["inventory"]["rations"], 17)
        self.assertEqual(engine.site_view("frontier_port")["inventory"]["rations"], 6)
        self.assertEqual(engine.state.totals()["rations"], 23)

    def test_policy_proposal_rejects_remote_stock_and_invalid_amount(self):
        engine = CausalEngine(p3_fixture())
        for route, commodity, amount in (
            ("missing", "rations", 3),
            ("corridor_a", "energy_j", 3),
            ("corridor_a", "rations", 0),
            ("corridor_a", "rations", True),
        ):
            with self.assertRaises(FeasibilityError):
                prepare_relief_proposal(
                    engine, institution_id="relief_council",
                    proposer_id="governor", route_id=route,
                    commodity=commodity, amount=amount, expires_s=30)

    def test_institutional_rules_are_data_not_polity_name_branches(self):
        world = p3_fixture()
        world.sites["union_depot"].polity_id = "fixture_different_culture"
        world.institutions["relief_council"].polity_id = "fixture_different_culture"
        engine, motion_id = self.make_engine(world=world)
        self.approve(engine, motion_id)
        receipt = engine.dispatch_ratified_relief(
            motion_id, "governor", cause="actor:ship")
        self.assertTrue(receipt.effect["institutionally_authorized"])
        self.assertEqual(engine.polity_view("fixture_different_culture")
                         ["available"]["rations"], 17)
        self.assertEqual(engine.state.totals()["rations"], 23)

    def test_unconstitutional_institution_cannot_initialize(self):
        world = p3_fixture()
        world.institutions["relief_council"] = Institution(
            "relief_council", "union_depot",
            ("governor", "member_a"), quorum=1,
            approval_threshold=2, polity_id="fixture_union")
        with self.assertRaises(ValueError):
            CausalEngine(world)

    def test_original_p0_state_hash_preserved_with_empty_p3_fields(self):
        from simulation.runtime.gumas_unified.scenario import run_experiment
        self.assertEqual(
            run_experiment()["evidence"]["final_state"],
            "518eff3927c3f38d7c6e8faa46c011d7f411ce410357cf6b92f83abcb3e1e11c",
        )


if __name__ == "__main__":
    unittest.main()
