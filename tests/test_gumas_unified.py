"""Contract tests: synthetic GUMAS Unified P0. Stdlib unittest only."""
from __future__ import annotations

from copy import deepcopy
import unittest

from simulation.runtime.gumas_unified import (
    CausalEngine, FeasibilityError, PhysicsProfile,
    observe_legacy_political_snapshot, verify_ledger,
)
from simulation.runtime.gumas_unified.scenario import fixture, run_experiment


class UnifiedCausalTests(unittest.TestCase):
    def make_engine(self):
        return CausalEngine(fixture())

    def test_true_reproducibility_and_ledger_chain(self):
        first = run_experiment()
        second = run_experiment()
        self.assertEqual(first, second)
        e = first["evidence"]
        self.assertTrue(e["ledger_valid"])
        self.assertEqual(e["authority"], "L2_synthetic_only")
        self.assertEqual(e["resource_totals"], {"energy_j": 110000, "rations": 23})
        self.assertEqual([row["kind"] for row in e["ledger"]],
                         ["route_capacity_changed", "shipment_departed", "report_sent",
                          "clock_advanced", "report_arrival", "cargo_arrival"])

    def test_causality_and_information_delay(self):
        result = run_experiment()
        self.assertEqual(result["before_signal"]["received_reports"], [])
        self.assertEqual(len(result["after_signal"]["received_reports"]), 1)
        report = result["after_signal"]["received_reports"][0]
        self.assertEqual((report["sent_s"], report["received_s"]), (0, 4))
        self.assertEqual(result["departure"]["destination"]["inventory"]["rations"], 3)
        self.assertEqual(result["arrival"]["destination"]["inventory"]["rations"], 6)

    def test_macro_and_micro_reconcile(self):
        result = run_experiment()
        departure = result["departure"]
        self.assertEqual(departure["origin"]["inventory"]["rations"], 17)
        self.assertEqual(departure["origin_polity"]["available"]["rations"], 17)
        self.assertEqual(departure["destination_polity"]["incoming"]["rations"], 3)
        self.assertEqual(departure["destination_polity"]["available"]["rations"], 3)
        arrival = result["arrival"]
        self.assertEqual(arrival["destination_polity"]["available"]["rations"], 6)
        self.assertEqual(arrival["destination_polity"]["incoming"], {})
        self.assertEqual(result["evidence"]["resource_totals"]["rations"], 23)

    def test_different_agent_choice_different_macro_history(self):
        dispatch, hold = run_experiment(governor_choice="dispatch"), run_experiment(
            governor_choice="hold")
        self.assertNotEqual(dispatch["evidence"]["final_state"],
                            hold["evidence"]["final_state"])
        self.assertEqual(dispatch["arrival"]["destination"]["inventory"]["rations"], 6)
        self.assertEqual(hold["arrival"]["destination"]["inventory"]["rations"], 3)
        self.assertEqual(dispatch["evidence"]["resource_totals"],
                         hold["evidence"]["resource_totals"])

    def test_failed_actions_are_atomic(self):
        engine = self.make_engine()
        baseline = engine.state.digest()
        failures = (
            lambda: engine.dispatch("governor", "corridor_a", "rations", 7,
                                    cause="test:excess-capacity"),
            lambda: engine.dispatch("observer", "corridor_a", "rations", 1,
                                    cause="test:remote-actor"),
            lambda: engine.dispatch("governor", "corridor_a", "rations", 21,
                                    cause="test:missing-stock"),
            lambda: engine.send_report("observer", "governor", "corridor_a",
                                       "hello", cause="test:no-reverse-path"),
            lambda: engine.dispatch("governor", "missing", "rations", 1,
                                    cause="test:missing-path"),
            lambda: engine.advance_to(-1),
        )
        for fail in failures:
            with self.assertRaises(FeasibilityError):
                fail()
            self.assertEqual(engine.state.digest(), baseline)
            self.assertEqual(engine.ledger, [])

    def test_energy_and_capacity_are_accounted(self):
        engine = self.make_engine()
        engine.disrupt_route("corridor_a", 4, cause="fixture:disruption")
        engine.dispatch("governor", "corridor_a", "rations", 3,
                        cause="actor:dispatch")
        engine.send_report("governor", "observer", "corridor_a", "status",
                           cause="actor:report")
        self.assertEqual(engine.state.heat_j, 4800)
        self.assertEqual(engine.state.totals(), {"energy_j": 110000, "rations": 23})
        with self.assertRaises(FeasibilityError):
            engine.dispatch("governor", "corridor_a", "rations", 2,
                            cause="test:capacity")
        self.assertEqual(engine.state.capacity_used["corridor_a@0"], 3)

    def test_institutional_rule_violation_is_not_a_physics_violation(self):
        engine = self.make_engine()
        receipt = engine.dispatch("local_dissenter", "corridor_a", "rations", 1,
                                  cause="actor:unauthorized-use")
        self.assertFalse(receipt.effect["institutionally_authorized"])
        self.assertEqual(engine.state.in_transit[
            receipt.effect["shipment_id"]].amount, 1)

    def test_snapshot_cannot_mutate_kernel(self):
        engine = self.make_engine()
        snapshot = engine.state
        snapshot.sites["union_depot"].inventory["rations"] = 99999
        snapshot.corridors["corridor_a"].enabled = False
        self.assertEqual(engine.state.sites["union_depot"].inventory["rations"], 20)
        self.assertTrue(engine.state.corridors["corridor_a"].enabled)

    def test_external_receipts_cannot_mutate_committed_ledger(self):
        engine = self.make_engine()
        receipt = engine.disrupt_route("corridor_a", 4,
                                      cause="fixture:disruption")
        receipt.effect["new_capacity"] = 999
        public_history = engine.ledger
        public_history[0].effect["new_capacity"] = 888
        public_history.clear()
        self.assertEqual(engine.ledger[0].effect["new_capacity"], 4)
        self.assertTrue(verify_ledger(engine.ledger, engine.initial_hash,
                                      engine.state.digest()))

    def test_ledger_tampering_detected(self):
        engine = self.make_engine()
        engine.disrupt_route("corridor_a", 4, cause="fixture:disruption")
        self.assertTrue(verify_ledger(engine.ledger, engine.initial_hash,
                                      engine.state.digest()))
        altered = deepcopy(engine.ledger)
        altered[0].effect["new_capacity"] = 400
        self.assertFalse(verify_ledger(altered, engine.initial_hash,
                                       engine.state.digest()))

    def test_physics_profile_rejects_unjustified_ftl(self):
        world = fixture()
        world.corridors["corridor_a"].signal_speed_km_s = 400000
        with self.assertRaisesRegex(ValueError, "signaling"):
            CausalEngine(world)
        with self.assertRaisesRegex(ValueError, "superluminal"):
            CausalEngine(fixture(), PhysicsProfile(signal_speed_ceiling_km_s=500000))

    def test_no_energy_infinite_motion(self):
        world = fixture()
        world.sites["union_depot"].inventory["energy_j"] = 1
        engine = CausalEngine(world)
        before = engine.state.digest()
        with self.assertRaisesRegex(FeasibilityError, "energy"):
            engine.dispatch("governor", "corridor_a", "rations", 1,
                            cause="test:no-energy")
        self.assertEqual(before, engine.state.digest())

    def test_legacy_political_bridge_is_read_only(self):
        raw = {"factions": {"galactic_union": {
            "economic_strength": 0.52, "military_strength": 0.4,
            "trust_scores": {"velar_imperium": 0.13},
            "leader_id": "example-leader"}}}
        observed = observe_legacy_political_snapshot(raw)
        self.assertEqual(observed["authority"], "noncanonical_read_only")
        self.assertTrue(observed["not_a_resource_ledger"])
        self.assertEqual(observed["polities"]["galactic_union"]["economic_strength"], 0.52)
        observed["polities"]["galactic_union"]["trust_scores"]["velar_imperium"] = 1.0
        self.assertEqual(raw["factions"]["galactic_union"]["trust_scores"]
                         ["velar_imperium"], 0.13)
        with self.assertRaises(ValueError):
            observe_legacy_political_snapshot({"factions": []})


if __name__ == "__main__":
    unittest.main()
