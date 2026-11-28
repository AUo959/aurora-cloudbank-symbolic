"""Contract tests: explicit corridor closure in GUMAS Unified P0.

Resolves the open design question archived from tracker #1711: a route
disrupted to zero capacity is not a closure. Capacity stays a positive
integer (the P0 invariant), ``disrupt_route`` refuses zero up front, and a
full closure is the explicit ``close_route`` / ``reopen_route`` transition on
``Corridor.enabled``. Synthetic L2 only. Stdlib unittest only.
"""
from __future__ import annotations

import unittest

from simulation.runtime.gumas_unified import CausalEngine, FeasibilityError, verify_ledger
from simulation.runtime.gumas_unified.scenario import fixture

ZERO_MESSAGE = "capacity must be a positive integer; use close_route for a full closure"


def _engine() -> CausalEngine:
    return CausalEngine(fixture(), run_id="synthetic-p0-closure")


def _snapshot(engine: CausalEngine):
    return engine.state.digest(), list(engine.ledger)


class ZeroCapacityIsRefused(unittest.TestCase):
    def test_zero_and_invalid_capacity_fail_fast_without_side_effects(self):
        for value in (0, -1, True, False, 1.0, None, "4"):
            with self.subTest(value=value):
                engine = _engine()
                before = _snapshot(engine)
                with self.assertRaises(FeasibilityError) as caught:
                    engine.disrupt_route("corridor_a", value, cause="fixture:zero")
                self.assertEqual(str(caught.exception), ZERO_MESSAGE)
                self.assertEqual(_snapshot(engine), before)

    def test_zero_is_refused_before_provenance_or_route_lookup(self):
        engine = _engine()
        for route_id, cause in (("corridor_a", "actor:not-fixture"),
                                ("no_such_corridor", "fixture:zero")):
            with self.subTest(route_id=route_id, cause=cause):
                with self.assertRaisesRegex(FeasibilityError, "^capacity must be"):
                    engine.disrupt_route(route_id, 0, cause=cause)

    def test_minimum_positive_capacity_is_still_accepted(self):
        engine = _engine()
        receipt = engine.disrupt_route("corridor_a", 1, cause="fixture:squeeze")
        self.assertEqual(receipt.effect, {"route_id": "corridor_a", "old_capacity": 6,
                                          "new_capacity": 1})


class ExplicitClosure(unittest.TestCase):
    def test_close_route_records_receipt_and_keeps_capacity(self):
        engine = _engine()
        receipt = engine.close_route("corridor_a", cause="fixture:closure")
        self.assertEqual(receipt.kind, "route_closed")
        self.assertIsNone(receipt.actor_id)
        self.assertEqual(receipt.effect, {"route_id": "corridor_a", "enabled": False,
                                          "capacity_units_per_window": 6})
        route = engine.state.corridors["corridor_a"]
        self.assertIs(route.enabled, False)
        self.assertEqual(route.capacity_units_per_window, 6)
        self.assertTrue(verify_ledger(engine.ledger, engine.initial_hash,
                                      engine.state.digest()))

    def test_closure_blocks_both_cargo_and_signals(self):
        # This is what separates a closure from a zero-capacity corridor:
        # capacity only gates cargo, closure gates every use of the route.
        engine = _engine()
        engine.close_route("corridor_a", cause="fixture:closure")
        before = _snapshot(engine)
        with self.assertRaisesRegex(FeasibilityError, "^corridor is inaccessible$"):
            engine.dispatch("governor", "corridor_a", "rations", 1, cause="actor:try")
        with self.assertRaisesRegex(FeasibilityError, "^corridor is inaccessible$"):
            engine.send_report("governor", "observer", "corridor_a", "status",
                               cause="actor:try")
        self.assertEqual(_snapshot(engine), before)

    def test_in_transit_cargo_and_signals_still_arrive(self):
        engine = _engine()
        engine.dispatch("governor", "corridor_a", "rations", 3, cause="actor:ship")
        engine.send_report("governor", "observer", "corridor_a", "sent", cause="actor:tell")
        engine.close_route("corridor_a", cause="fixture:closure")
        arrivals = engine.advance_to(12)
        self.assertEqual({r.kind for r in arrivals} - {"clock_advanced"},
                         {"report_arrival", "cargo_arrival"})
        self.assertEqual(engine.site_view("frontier_port")["inventory"]["rations"], 6)
        self.assertEqual(engine.state.in_transit, {})

    def test_reopen_restores_prior_capacity(self):
        engine = _engine()
        engine.disrupt_route("corridor_a", 4, cause="fixture:squeeze")
        engine.close_route("corridor_a", cause="fixture:closure")
        engine.disrupt_route("corridor_a", 2, cause="fixture:repair-plan")
        receipt = engine.reopen_route("corridor_a", cause="fixture:reopen")
        self.assertEqual(receipt.kind, "route_reopened")
        self.assertEqual(receipt.effect, {"route_id": "corridor_a", "enabled": True,
                                          "capacity_units_per_window": 2})
        engine.dispatch("governor", "corridor_a", "rations", 2, cause="actor:ship")
        with self.assertRaisesRegex(FeasibilityError, "capacity"):
            engine.dispatch("governor", "corridor_a", "rations", 1, cause="actor:ship")
        self.assertEqual([r.kind for r in engine.ledger],
                         ["route_capacity_changed", "route_closed",
                          "route_capacity_changed", "route_reopened",
                          "shipment_departed"])

    def test_redundant_or_unprovenanced_transitions_are_refused(self):
        engine = _engine()
        cases = [
            (lambda: engine.reopen_route("corridor_a", cause="fixture:x"),
             "^corridor is already open$"),
            (lambda: engine.close_route("corridor_a", cause="actor:x"),
             "^external field changes require fixture provenance$"),
            (lambda: engine.close_route("nowhere", cause="fixture:x"),
             "^unknown corridor$"),
        ]
        for call, pattern in cases:
            before = _snapshot(engine)
            with self.subTest(pattern=pattern):
                with self.assertRaisesRegex(FeasibilityError, pattern):
                    call()
                self.assertEqual(_snapshot(engine), before)
        engine.close_route("corridor_a", cause="fixture:closure")
        before = _snapshot(engine)
        with self.assertRaisesRegex(FeasibilityError, "^corridor is already closed$"):
            engine.close_route("corridor_a", cause="fixture:again")
        self.assertEqual(_snapshot(engine), before)


if __name__ == "__main__":
    unittest.main()
