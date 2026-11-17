"""P6 seatless association and material mandates: deterministic safety gates."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json
import unittest

from simulation.runtime.gumas_unified import CausalEngine, FeasibilityError
from simulation.runtime.gumas_unified.federated_actions import association_view
from simulation.runtime.gumas_unified.federated_model import (
    Association, Charter, Mandate, charter_terms, fingerprint, mandate_terms,
)
from simulation.runtime.gumas_unified.federated_scenario import (
    federated_fixture, run_p6, run_remote_initiative,
)
from simulation.runtime.gumas_unified.governance_scenario import run_p4
from simulation.runtime.gumas_unified.political_scenario import run_p3
from simulation.runtime.gumas_unified.distributed_scenario import run_distributed
from simulation.runtime.gumas_unified.scenario import run_experiment


def setup_engine(*, expires_s=42, accept=True, confirm=False):
    engine = CausalEngine(federated_fixture(), run_id="synthetic-p6-acceptance")
    offer = engine.offer_charter(
        "governor", "member_b", "Voluntary reciprocal relief",
        "corridor_a", expires_s=expires_s, cause="actor:invite")
    cid = offer.effect["charter_id"]
    engine.advance_to(4)
    engine.respond_charter(
        cid, "member_b", accept, "return_signal",
        cause="actor:individual-invitee-choice")
    engine.advance_to(8)
    aid = engine.state.charters[cid].association_id
    if confirm and aid is not None:
        engine.confirm_association(
            aid, "governor", cause="actor:founder-confirms")
        engine.advance_to(12)
    return engine, cid, aid


def proposal(engine, association_id, proposer_id="governor", *,
             amount=3, expires_s=44, commodity="rations"):
    route = "corridor_a" if proposer_id == "governor" else "return_signal"
    receipt = engine.propose_mandate(
        association_id, proposer_id, route, route, commodity, amount,
        expires_s=expires_s, cause="actor:coordinated-proposal")
    return receipt.effect["mandate_id"]


def respond(engine, mandate_id, *, approve=True):
    mandate = engine.state.mandates[mandate_id]
    engine.advance_to(mandate.offer_due_s)
    return_route = ("return_signal" if mandate.voter_id == "member_b"
                    else "corridor_a")
    engine.respond_mandate(
        mandate_id, mandate.voter_id, approve, return_route,
        cause="actor:independent-mandate-choice")
    engine.advance_to(engine.state.mandates[mandate_id].vote_due_s)


class P6SeatlessAssociationTests(unittest.TestCase):
    def test_charter_and_mandate_yes_preserve_physical_conservation(self):
        result = run_p6()
        self.assertTrue(result["association_formed"])
        self.assertTrue(result["evidence"]["ledger_valid"])
        self.assertEqual(result["origin"]["inventory"]["rations"], 17)
        self.assertEqual(result["destination"]["inventory"]["rations"], 6)
        self.assertEqual(result["evidence"]["resource_totals"],
                         {"energy_j": 110000, "rations": 23})
        self.assertIsNone(result["association"]["permanent_seat"])
        self.assertTrue(result["shipment"]["association_approved"])
        self.assertTrue(result["shipment"]["site_dispatch_authorized"])
        self.assertFalse(result["shipment"]["source_canon_promoted"])

    def test_charter_rejection_prevents_institution_creation_and_transfer(self):
        result = run_p6(charter_accept=False)
        self.assertFalse(result["association_formed"])
        self.assertEqual(result["origin"]["inventory"]["rations"], 20)
        self.assertEqual(result["destination"]["inventory"]["rations"], 3)
        self.assertTrue(result["evidence"]["ledger_valid"])
        self.assertFalse(any(
            e["kind"] == "seatless_mandate_dispatched"
            for e in result["evidence"]["ledger"]))

    def test_remote_negative_mandate_blocks_dispatch_even_after_formation(self):
        result = run_p6(mandate_approve=False)
        self.assertTrue(result["association_formed"])
        self.assertIsNone(result["shipment"])
        self.assertEqual(result["origin"]["inventory"]["rations"], 20)
        self.assertEqual(result["destination"]["inventory"]["rations"], 3)
        self.assertEqual(next(iter(result["association"]["mandates"].values()))
                         ["status"], "rejected")
        self.assertTrue(result["evidence"]["ledger_valid"])

    def test_remote_member_can_initiate_without_permanent_council_seat(self):
        result = run_remote_initiative()
        self.assertTrue(result["evidence"]["ledger_valid"])
        self.assertIsNone(result["association"]["permanent_seat"])
        self.assertEqual(result["execution"]["custodian_id"], "member_b")
        self.assertTrue(result["execution"]["association_approved"])
        self.assertFalse(result["execution"]["site_dispatch_authorized"])
        self.assertEqual(result["origin"]["inventory"]["rations"], 2)
        self.assertEqual(result["destination"]["inventory"]["rations"], 21)
        self.assertEqual(result["evidence"]["resource_totals"]["rations"], 23)

    def test_foundation_not_implied_by_outbound_invitation(self):
        engine = CausalEngine(federated_fixture())
        cid = engine.offer_charter(
            "governor", "member_b", "Voluntary alliance",
            "corridor_a", expires_s=42, cause="actor:send-charter").effect["charter_id"]
        self.assertEqual(engine.actor_view("member_b")["received_reports"], [])
        self.assertEqual(engine.state.associations, {})
        self.assertEqual(engine.state.charters[cid].status, "offer_inflight")
        engine.advance_to(3)
        self.assertEqual(engine.state.associations, {})

    def test_invitee_cannot_accept_without_delivered_charter(self):
        engine = CausalEngine(federated_fixture())
        cid = engine.offer_charter(
            "governor", "member_b", "Voluntary alliance",
            "corridor_a", expires_s=42, cause="actor:invite").effect["charter_id"]
        before, count = engine.state.digest(), len(engine.ledger)
        with self.assertRaises(FeasibilityError):
            engine.respond_charter(
                cid, "member_b", True, "return_signal", cause="actor:premature")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(len(engine.ledger), count)
        engine.advance_to(4)
        self.assertEqual(engine.actor_view("member_b")["received_reports"][0]
                         ["terms"]["purpose"], "Voluntary alliance")

    def test_association_only_formed_after_received_return_consent(self):
        engine = CausalEngine(federated_fixture())
        cid = engine.offer_charter(
            "governor", "member_b", "Voluntary alliance",
            "corridor_a", expires_s=42, cause="actor:invite").effect["charter_id"]
        engine.advance_to(4)
        engine.respond_charter(cid, "member_b", True, "return_signal",
                               cause="actor:independent-consent")
        engine.advance_to(7)
        self.assertEqual(engine.state.associations, {})
        self.assertEqual(engine.actor_view("governor")["received_reports"], [])
        engine.advance_to(8)
        self.assertEqual(len(engine.state.associations), 1)
        self.assertEqual(engine.actor_view("governor")["received_reports"][0]
                         ["decision"], True)
        self.assertEqual(engine.state.charters[cid].status, "formed")

    def test_charter_consent_cannot_be_replayed(self):
        engine, cid, aid = setup_engine()
        before, receipts = engine.state.digest(), engine.ledger
        with self.assertRaises(FeasibilityError):
            engine.respond_charter(
                cid, "member_b", True, "return_signal", cause="actor:repeat")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.ledger, receipts)
        self.assertEqual(len(engine.state.associations), 1)

    def test_second_active_charter_for_same_pair_refused(self):
        engine, _, aid = setup_engine()
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "already"):
            engine.offer_charter(
                "governor", "member_b", "Duplicate charter",
                "corridor_a", expires_s=45, cause="actor:reinvite")
        self.assertEqual(engine.state.digest(), before)

    def test_late_charter_acceptance_is_not_retroactive_formation(self):
        engine = CausalEngine(federated_fixture())
        cid = engine.offer_charter(
            "governor", "member_b", "Deadline-bound charter",
            "corridor_a", expires_s=6, cause="actor:invite").effect["charter_id"]
        engine.advance_to(4)
        engine.respond_charter(cid, "member_b", True, "return_signal",
                               cause="actor:yes-before-deadline")
        engine.advance_to(6)
        self.assertEqual(engine.state.charters[cid].status, "expired")
        engine.advance_to(8)
        self.assertEqual(engine.state.associations, {})
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_absent_reverse_communications_path_refuses_consent(self):
        engine = CausalEngine(federated_fixture())
        cid = engine.offer_charter(
            "governor", "member_b", "Path-required charter",
            "corridor_a", expires_s=42, cause="actor:invite").effect["charter_id"]
        engine.advance_to(4)
        before = engine.state.digest()
        with self.assertRaises(FeasibilityError):
            engine.respond_charter(cid, "member_b", True, "corridor_a",
                                   cause="actor:wrong-way")
        self.assertEqual(engine.state.digest(), before)

    def test_unpowered_return_signal_cannot_convey_foundation(self):
        world = federated_fixture()
        world.sites["frontier_port"].inventory["energy_j"] = 0
        engine = CausalEngine(world)
        cid = engine.offer_charter(
            "governor", "member_b", "Need power",
            "corridor_a", expires_s=42, cause="actor:invite").effect["charter_id"]
        engine.advance_to(4)
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "energy"):
            engine.respond_charter(cid, "member_b", True, "return_signal",
                                   cause="actor:unpowered")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.state.associations, {})

    def test_remote_member_knows_formation_only_after_confirmation(self):
        engine, cid, aid = setup_engine()
        self.assertTrue(aid)
        before = engine.actor_view("member_b")
        self.assertFalse(any(r["kind"] == "seatless_association_confirm"
                             for r in before["received_reports"]))
        engine.confirm_association(
            aid, "governor", cause="actor:explicit-formation-confirmation")
        engine.advance_to(11)
        self.assertFalse(engine.state.associations[aid].confirmed_to_invitee)
        engine.advance_to(12)
        after = engine.actor_view("member_b")
        self.assertTrue(engine.state.associations[aid].confirmed_to_invitee)
        self.assertTrue(any(r["kind"] == "seatless_association_confirm"
                            for r in after["received_reports"]))

    def test_remote_member_cannot_propose_until_knowing_formation(self):
        engine, cid, aid = setup_engine()
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "confirmation"):
            proposal(engine, aid, "member_b")
        self.assertEqual(engine.state.digest(), before)
        engine.confirm_association(aid, "governor", cause="actor:notify")
        engine.advance_to(11)
        with self.assertRaisesRegex(FeasibilityError, "confirmation"):
            proposal(engine, aid, "member_b")
        engine.advance_to(12)
        mid = proposal(engine, aid, "member_b")
        self.assertEqual(engine.state.mandates[mid].proposer_id, "member_b")

    def test_founder_cannot_forge_repeated_formation_confirmation(self):
        engine, _, aid = setup_engine()
        engine.confirm_association(aid, "governor", cause="actor:first")
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "already"):
            engine.confirm_association(aid, "governor", cause="actor:repeat")
        self.assertEqual(engine.state.digest(), before)

    def test_mandate_requires_actual_delivered_public_terms(self):
        engine, _, aid = setup_engine()
        mid = proposal(engine, aid)
        before = engine.state.digest()
        with self.assertRaises(FeasibilityError):
            engine.respond_mandate(mid, "member_b", True, "return_signal",
                                  cause="actor:uninformed")
        self.assertEqual(engine.state.digest(), before)
        engine.advance_to(12)
        notice = [r for r in engine.actor_view("member_b")["received_reports"]
                  if r["kind"] == "seatless_mandate_offer"][0]
        self.assertEqual(notice["terms"]["commodity"], "rations")
        self.assertEqual(notice["terms"]["amount"], 3)
        self.assertEqual(notice["terms"]["expires_s"], 44)
        self.assertEqual(notice["terms_sha256"],
                         fingerprint(notice["terms"]))

    def test_sent_mandate_consent_is_not_counted_until_arrival(self):
        engine, _, aid = setup_engine()
        mid = proposal(engine, aid)
        engine.advance_to(12)
        engine.respond_mandate(mid, "member_b", True, "return_signal",
                               cause="actor:yes")
        engine.advance_to(15)
        self.assertEqual(engine.state.mandates[mid].status, "vote_inflight")
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "not an active"):
            engine.execute_mandate(mid, "governor", cause="actor:too-early")
        self.assertEqual(engine.state.digest(), before)
        engine.advance_to(16)
        self.assertEqual(engine.state.mandates[mid].status, "authorized")
        self.assertEqual(engine.actor_view("governor")["received_reports"][-1]
                         ["decision"], True)

    def test_mandate_acceptance_does_not_auto_dispatch(self):
        engine, _, aid = setup_engine()
        mid = proposal(engine, aid)
        respond(engine, mid)
        self.assertEqual(engine.state.mandates[mid].status, "authorized")
        self.assertEqual(engine.state.in_transit, {})
        self.assertEqual(engine.site_view("union_depot")["inventory"]["rations"], 20)

    def test_mandate_negative_response_preserves_stock(self):
        engine, _, aid = setup_engine()
        mid = proposal(engine, aid)
        respond(engine, mid, approve=False)
        self.assertEqual(engine.state.mandates[mid].status, "rejected")
        with self.assertRaises(FeasibilityError):
            engine.execute_mandate(mid, "governor", cause="actor:reject-override")
        self.assertEqual(engine.state.totals()["rations"], 23)
        self.assertEqual(engine.state.in_transit, {})

    def test_late_mandate_vote_does_not_reopen_expired_authority(self):
        engine, _, aid = setup_engine()
        mid = proposal(engine, aid, expires_s=14)
        engine.advance_to(12)
        engine.respond_mandate(mid, "member_b", True, "return_signal",
                               cause="actor:before-deadline")
        engine.advance_to(14)
        self.assertEqual(engine.state.mandates[mid].status, "expired")
        engine.advance_to(16)
        self.assertEqual(engine.state.mandates[mid].status, "expired")
        self.assertFalse(any(e["kind"] == "seatless_mandate_dispatched"
                             for e in engine.evidence()["ledger"]))

    def test_mandate_exact_expiry_refuses_received_yes(self):
        engine, _, aid = setup_engine()
        mid = proposal(engine, aid, expires_s=16)
        engine.advance_to(12)
        engine.respond_mandate(mid, "member_b", True, "return_signal",
                               cause="actor:exact-expiry")
        engine.advance_to(16)
        self.assertEqual(engine.state.mandates[mid].status, "expired")
        self.assertIsNone(engine.state.mandates[mid].authorized_at_s)

    def test_mandate_cannot_be_fulfilled_twice(self):
        engine, _, aid = setup_engine()
        mid = proposal(engine, aid)
        respond(engine, mid)
        engine.execute_mandate(mid, "governor", cause="actor:first-dispatch")
        before, ledger = engine.state.digest(), engine.ledger
        with self.assertRaises(FeasibilityError):
            engine.execute_mandate(mid, "governor", cause="actor:duplicate-dispatch")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.ledger, ledger)

    def test_custodian_must_be_the_explicit_local_proposer(self):
        engine, _, aid = setup_engine()
        mid = proposal(engine, aid)
        respond(engine, mid)
        before = engine.state.digest()
        with self.assertRaises(FeasibilityError):
            engine.execute_mandate(mid, "member_b", cause="actor:wrong-custodian")
        self.assertEqual(engine.state.digest(), before)

    def test_approved_mandate_without_stock_fails_physically(self):
        world = federated_fixture()
        world.sites["union_depot"].inventory["rations"] = 1
        engine = CausalEngine(world)
        cid = engine.offer_charter(
            "governor", "member_b", "Relief pact",
            "corridor_a", expires_s=42, cause="actor:invite").effect["charter_id"]
        engine.advance_to(4)
        engine.respond_charter(cid, "member_b", True, "return_signal",
                               cause="actor:yes")
        engine.advance_to(8)
        aid = engine.state.charters[cid].association_id
        mid = proposal(engine, aid)
        respond(engine, mid)
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "stock"):
            engine.execute_mandate(mid, "governor", cause="actor:no-goods")
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(engine.state.totals()["rations"], 4)

    def test_approved_mandate_respects_existing_cargo_capacity(self):
        engine, _, aid = setup_engine()
        mid = proposal(engine, aid, amount=7)
        respond(engine, mid)
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "capacity"):
            engine.execute_mandate(mid, "governor", cause="actor:too-big")
        self.assertEqual(engine.state.digest(), before)

    def test_approved_mandate_lacks_cargo_energy_fails_atomically(self):
        engine, _, aid = setup_engine()
        mid = proposal(engine, aid, amount=6)
        respond(engine, mid)
        # P0 permits explicit disruptive fixture changes of capacity, but not
        # arbitrary resource production. Six rations are physically possible,
        # but cargo energy > source remaining would require a distinct fixture.
        world = federated_fixture()
        world.sites["union_depot"].inventory["energy_j"] = 5500
        limited = CausalEngine(world, run_id="synthetic-p6-low-power")
        cid = limited.offer_charter(
            "governor", "member_b", "Low-energy pact",
            "corridor_a", expires_s=42, cause="actor:invite").effect["charter_id"]
        limited.advance_to(4)
        limited.respond_charter(cid, "member_b", True, "return_signal",
                                cause="actor:yes")
        limited.advance_to(8)
        aid2 = limited.state.charters[cid].association_id
        mid2 = proposal(limited, aid2, amount=3)
        respond(limited, mid2)
        before = limited.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "energy"):
            limited.execute_mandate(mid2, "governor", cause="actor:no-fuel")
        self.assertEqual(limited.state.digest(), before)

    def test_other_p0_shipment_can_exhaust_shared_corridor(self):
        engine, _, aid = setup_engine()
        mid = proposal(engine, aid, amount=3)
        respond(engine, mid)
        engine.dispatch(
            "local_dissenter", "corridor_a", "rations", 4,
            cause="actor:competing-material-use")
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "capacity"):
            engine.execute_mandate(mid, "governor", cause="actor:overloaded")
        self.assertEqual(engine.state.digest(), before)

    def test_current_outcomes_are_not_polity_label_specific(self):
        world = federated_fixture()
        world.sites["union_depot"].polity_id = "fictional_river_culture"
        world.sites["frontier_port"].polity_id = "fictional_orbital_culture"
        world.institutions["relief_council"].polity_id = "fictional_river_culture"
        engine = CausalEngine(world)
        cid = engine.offer_charter(
            "governor", "member_b", "Cross polity compact",
            "corridor_a", expires_s=42, cause="actor:invite").effect["charter_id"]
        engine.advance_to(4)
        engine.respond_charter(cid, "member_b", True, "return_signal",
                               cause="actor:join")
        engine.advance_to(8)
        aid = engine.state.charters[cid].association_id
        mid = proposal(engine, aid)
        respond(engine, mid)
        engine.execute_mandate(mid, "governor", cause="actor:dispatch")
        engine.advance_to(28)
        self.assertEqual(engine.site_view("frontier_port")["inventory"]["rations"], 6)
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_association_does_not_mutate_p4_institution_roles(self):
        engine, _, aid = setup_engine()
        v = association_view(engine, aid)
        self.assertIsNone(v["permanent_seat"])
        self.assertEqual(set(v["member_sites"].values()),
                         {"union_depot", "frontier_port"})
        self.assertEqual(engine.state.institutions["relief_council"].seat_site_id,
                         "union_depot")
        self.assertEqual(engine.state.institutions["relief_council"].members,
                         ("governor", "member_a", "member_b"))
        self.assertFalse(v["canon_authority"])

    def test_operator_association_view_cannot_mutate_l2_state(self):
        engine, _, aid = setup_engine()
        before = engine.state.digest()
        view = association_view(engine, aid)
        view["members"].clear()
        view["member_sites"]["governor"] = "tampered"
        self.assertEqual(engine.state.digest(), before)
        self.assertEqual(len(engine.state.associations[aid].members), 2)

    def test_original_p0_to_p5_scenarios_and_hashes_unchanged(self):
        p0 = run_experiment()
        self.assertEqual(p0["evidence"]["final_state"],
                         "518eff3927c3f38d7c6e8faa46c011d7f411ce410357cf6b92f83abcb3e1e11c")
        self.assertTrue(run_p3()["evidence"]["ledger_valid"])
        self.assertTrue(run_p4("delegated")["evidence"]["ledger_valid"])
        self.assertTrue(run_distributed("veto")["evidence"]["ledger_valid"])

    def test_initial_unproven_association_is_rejected(self):
        world = federated_fixture()
        world.associations["forged"] = Association(
            "forged", "nonexistent", ("governor", "member_b"),
            0, "a"*64)
        with self.assertRaisesRegex(ValueError, "not founded"):
            CausalEngine(world)

    def test_initial_unproven_mandate_is_rejected(self):
        world = federated_fixture()
        world.mandates["forged"] = Mandate(
            "forged", "nonexistent", "governor", "member_b", "governor",
            "corridor_a", "corridor_a", "rations", 3, 0, 4, 45,
            "f"*64)
        with self.assertRaisesRegex(ValueError, "association"):
            CausalEngine(world)

    def test_empty_p6_state_does_not_alter_p5_fixture_digest(self):
        world = federated_fixture()
        payload = asdict(world)
        self.assertEqual(payload.pop("charters"), {})
        self.assertEqual(payload.pop("associations"), {})
        self.assertEqual(payload.pop("mandates"), {})
        for name in ("identity_bindings", "relief_motions", "remote_ballots"):
            if not payload[name]:
                payload.pop(name)
        enc = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.assertEqual(world.digest(), hashlib.sha256(enc).hexdigest())

    def _approved_mandate(self):
        engine, _, association_id = setup_engine()
        mandate_id = proposal(engine, association_id)
        respond(engine, mandate_id)
        receipt = engine.execute_mandate(
            mandate_id, "governor", cause="actor:well-formed-execution")
        return engine, mandate_id, receipt.effect["shipment_id"]

    def test_executed_mandate_carries_exact_cargo_provenance(self):
        engine, mandate_id, shipment_id = self._approved_mandate()
        mandate = engine.state.mandates[mandate_id]
        cargo = engine.state.in_transit[shipment_id]
        self.assertEqual(mandate.shipment_departed_s, cargo.departed_s)
        self.assertEqual(mandate.shipment_due_s, cargo.arrives_s)
        self.assertEqual((cargo.departed_s, cargo.arrives_s), (16, 28))
        self.assertTrue(engine.evidence()["ledger_valid"])

    def test_forged_executed_mandate_without_real_cargo_is_rejected(self):
        engine, mandate_id, _ = self._approved_mandate()
        snapshot = engine.state
        snapshot.mandates[mandate_id].shipment_id = "invented-shipment"
        with self.assertRaisesRegex(ValueError, "missing in-transit"):
            CausalEngine(snapshot)

    def test_phantom_or_mismatched_cargo_fields_are_rejected(self):
        engine, mandate_id, shipment_id = self._approved_mandate()
        for field, value in (("cargo_name", "fictitious_goods"),
                             ("route_id", "return_signal"),
                             ("amount", 2),
                             ("sender_id", "member_a"),
                             ("destination_id", "union_depot"),
                             ("departed_s", 15),
                             ("arrives_s", 29)):
            with self.subTest(field=field):
                snapshot = engine.state
                setattr(snapshot.in_transit[shipment_id], field, value)
                with self.assertRaises(ValueError):
                    CausalEngine(snapshot)

    def test_mandate_arrival_clock_cannot_be_forged(self):
        engine, mandate_id, _ = self._approved_mandate()
        for field, value in (("shipment_departed_s", 15),
                             ("shipment_due_s", 27),
                             ("shipment_due_s", 9999),
                             ("shipment_departed_s", None)):
            with self.subTest(field=field, value=value):
                snapshot = engine.state
                setattr(snapshot.mandates[mandate_id], field, value)
                with self.assertRaises(ValueError):
                    CausalEngine(snapshot)

    def test_completed_shipment_retains_valid_provenance_after_delivery(self):
        engine, mandate_id, shipment_id = self._approved_mandate()
        engine.advance_to(28)
        self.assertNotIn(shipment_id, engine.state.in_transit)
        mandate = engine.state.mandates[mandate_id]
        self.assertEqual(mandate.shipment_due_s, 28)
        self.assertTrue(engine.evidence()["ledger_valid"])
        for field, value in (("shipment_due_s", 29),
                             ("shipment_due_s", None),
                             ("shipment_departed_s", 17)):
            snapshot = engine.state
            setattr(snapshot.mandates[mandate_id], field, value)
            with self.assertRaises(ValueError):
                CausalEngine(snapshot)

    def test_pending_mandate_cannot_contain_shipment_metadata(self):
        engine, _, association_id = setup_engine()
        mandate_id = proposal(engine, association_id)
        snapshot = engine.state
        snapshot.mandates[mandate_id].shipment_id = "ghost"
        snapshot.mandates[mandate_id].shipment_departed_s = 8
        snapshot.mandates[mandate_id].shipment_due_s = 20
        with self.assertRaisesRegex(ValueError, "unexecuted"):
            CausalEngine(snapshot)

    def test_unacknowledged_charter_and_mandate_ballot_states_are_invalid(self):
        engine = CausalEngine(federated_fixture())
        charter_id = engine.offer_charter(
            "governor", "member_b", "Strict provenance",
            "corridor_a", expires_s=42, cause="actor:propose").effect["charter_id"]
        state = engine.state
        state.charters[charter_id].status = "response_inflight"
        with self.assertRaises(ValueError):
            CausalEngine(state)
        engine, _, association_id = setup_engine()
        mandate_id = proposal(engine, association_id)
        state = engine.state
        state.mandates[mandate_id].status = "authorized"
        with self.assertRaises(ValueError):
            CausalEngine(state)

    def test_unreceived_negative_vote_cannot_be_forced_into_rejection(self):
        engine, _, association_id = setup_engine()
        mandate_id = proposal(engine, association_id)
        snapshot = engine.state
        snapshot.mandates[mandate_id].status = "rejected"
        snapshot.mandates[mandate_id].vote_approve = True
        with self.assertRaises(ValueError):
            CausalEngine(snapshot)

    def test_all_seatless_entrypoints_reject_nonsynthetic_engine_runs(self):
        # P0 already rejects non-synthetic run IDs at construction.
        # Tampering after creation probes P6's additional defense in depth.
        engine = CausalEngine(federated_fixture(), run_id="synthetic-guard-test")
        engine.run_id = "operational-not-l2"
        calls = (
            lambda: engine.offer_charter(
                "governor", "member_b", "Unapproved", "corridor_a",
                expires_s=42, cause="operator:invalid"),
            lambda: engine.respond_charter(
                "fictional-charter", "member_b", True, "return_signal",
                cause="operator:invalid"),
            lambda: engine.confirm_association(
                "fictional-association", "governor",
                cause="operator:invalid"),
            lambda: engine.propose_mandate(
                "fictional-association", "governor", "corridor_a",
                "corridor_a", "rations", 3, expires_s=42,
                cause="operator:invalid"),
            lambda: engine.respond_mandate(
                "fictional-mandate", "member_b", True, "return_signal",
                cause="operator:invalid"),
            lambda: engine.execute_mandate(
                "fictional-mandate", "governor",
                cause="operator:invalid"),
            lambda: association_view(engine, "fictional-association"),
        )
        before, history = engine.state.digest(), engine.ledger
        for call in calls:
            with self.assertRaisesRegex(FeasibilityError, "synthetic L2"):
                call()
            self.assertEqual(engine.state.digest(), before)
            self.assertEqual(engine.ledger, history)

    def test_p6_clock_determinism_and_event_replay_checks(self):
        a, b = run_p6(), run_p6()
        self.assertEqual(a, b)
        self.assertTrue(a["evidence"]["ledger_valid"])
        kinds = [r["kind"] for r in a["evidence"]["ledger"]]
        for earlier, later in (
            ("seatless_charter_offered", "charter_offer_arrival"),
            ("charter_offer_arrival", "seatless_charter_response_sent"),
            ("seatless_charter_response_sent", "charter_response_arrival"),
            ("charter_response_arrival", "seatless_mandate_offered"),
            ("seatless_mandate_offered", "mandate_offer_arrival"),
            ("mandate_offer_arrival", "seatless_mandate_vote_sent"),
            ("seatless_mandate_vote_sent", "mandate_vote_arrival"),
            ("mandate_vote_arrival", "seatless_mandate_dispatched"),
            ("seatless_mandate_dispatched", "cargo_arrival"),
        ):
            self.assertLess(kinds.index(earlier), kinds.index(later))
        self.assertTrue(all("canon_promoted" not in r["kind"]
                            for r in a["evidence"]["ledger"]))

    def test_actor_knows_received_reply_not_inflight_intention(self):
        result = run_p6()
        self.assertFalse(any(
            r["kind"] == "seatless_mandate_response"
            for r in result["founder_before_vote"]["received_reports"]))
        self.assertTrue(any(
            r["kind"] == "seatless_mandate_response"
            and r["decision"] is True
            for r in result["founder_after_vote"]["received_reports"]))
        self.assertFalse(any(
            r["kind"] == "seatless_association_confirm"
            for r in result["remote_before_mandate"]["received_reports"]))
        self.assertTrue(any(
            r["kind"] == "seatless_association_confirm"
            for r in result["remote_after_mandate"]["received_reports"]))


if __name__ == "__main__":
    unittest.main()
