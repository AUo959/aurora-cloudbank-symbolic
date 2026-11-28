"""Characterization tests: GUMAS Unified P0 ``Universe.validate``.

Pins the observable contract of the foundational validator *before* it is
decomposed: accepted states, exact exception type and message for every
rejection site, first-failure ordering across sections, boundary values,
purity, and transactional rejection in the kernel. Synthetic L2 only.
Stdlib unittest only. These tests must pass unchanged on the original P0
head and on every descendant layer (P1-P6) as well as on the split candidate.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import itertools
import unittest

from simulation.runtime.gumas_unified import CausalEngine, PhysicsProfile
from simulation.runtime.gumas_unified.model import Universe
from simulation.runtime.gumas_unified.scenario import fixture

LIGHT_KM_S = 299792


def _base() -> Universe:
    return fixture()


def _inflight() -> Universe:
    """State with a shipment, both P0 event kinds, used capacity and heat."""
    engine = CausalEngine(fixture(), run_id="synthetic-p0-validator-characterization")
    engine.dispatch("governor", "corridor_a", "rations", 2, cause="test:dispatch")
    engine.send_report("governor", "observer", "corridor_a", "status",
                       cause="test:report")
    return engine.state


def _route(w: Universe):
    return w.corridors["corridor_a"]


def _ship(w: Universe):
    return next(iter(w.in_transit.values()))


# (case id, state builder, mutator, profile kwargs, exact expected message)
# Every ``raise`` site and every ``natural(...)`` call in P0 validate appears
# at least once. Kinds "bogus" etc. are chosen so the cases stay valid when
# later layers widen the accepted event-kind set.
FAULTS = [
    ("time_negative", _base, lambda w: setattr(w, "time_s", -1), {},
     "time_s must be a nonnegative integer"),
    ("heat_bool", _base, lambda w: setattr(w, "heat_j", True), {},
     "heat_j must be a nonnegative integer"),
    ("serial_float", _base, lambda w: setattr(w, "next_serial", 1.0), {},
     "next_serial must be a nonnegative integer"),
    ("signal_ceiling_zero", _base, None, {"signal_speed_ceiling_km_s": 0},
     "signal ceiling must be a positive integer"),
    ("cargo_ceiling_zero", _base, None, {"cargo_speed_ceiling_km_s": 0},
     "cargo ceiling must be a positive integer"),
    ("signal_superluminal", _base, None, {"signal_speed_ceiling_km_s": LIGHT_KM_S + 1},
     "P0 does not authorize superluminal signaling"),
    ("cargo_superluminal", _base, None, {"cargo_speed_ceiling_km_s": LIGHT_KM_S + 1},
     "P0 does not authorize superluminal cargo transport"),
    ("site_key_mismatch", _base,
     lambda w: w.sites.__setitem__("alias", w.sites["frontier_port"]), {},
     "invalid site identity"),
    ("site_polity_empty", _base,
     lambda w: setattr(w.sites["frontier_port"], "polity_id", ""), {},
     "invalid site identity"),
    ("commodity_empty", _base,
     lambda w: w.sites["frontier_port"].inventory.__setitem__("", 1), {},
     "empty commodity"),
    ("inventory_negative", _base,
     lambda w: w.sites["frontier_port"].inventory.__setitem__("rations", -1), {},
     "inventory frontier_port/rations must be a nonnegative integer"),
    ("actor_key_mismatch", _base,
     lambda w: w.actors.__setitem__("ghost", w.actors["observer"]), {},
     "invalid actor identity or site"),
    ("actor_site_absent", _base,
     lambda w: setattr(w.actors["observer"], "site_id", "nowhere"), {},
     "invalid actor identity or site"),
    ("actor_auth_site_absent", _base,
     lambda w: setattr(w.actors["observer"], "authorized_dispatch_sites", ("nowhere",)), {},
     "invalid actor authorization site"),
    ("route_key_mismatch", _base,
     lambda w: w.corridors.__setitem__("alias", _route(w)), {},
     "invalid route identity"),
    ("route_origin_absent", _base, lambda w: setattr(_route(w), "origin_id", "nowhere"), {},
     "route endpoint absent"),
    ("route_destination_absent", _base,
     lambda w: setattr(_route(w), "destination_id", "nowhere"), {},
     "route endpoint absent"),
    *[(f"route_{n}_zero", _base, (lambda n: lambda w: setattr(_route(w), n, 0))(n), {},
       f"{n} must be a positive integer")
      for n in ("distance_km", "cargo_speed_km_s", "signal_speed_km_s",
                "capacity_units_per_window", "window_seconds")],
    *[(f"route_{n}_negative", _base, (lambda n: lambda w: setattr(_route(w), n, -1))(n), {},
       f"{n} must be a nonnegative integer")
      for n in ("shipment_energy_j_per_unit_km", "signal_energy_j_per_km")],
    *[(f"route_enabled_{label}", _base,
       (lambda v: lambda w: setattr(_route(w), "enabled", v))(value), {},
       "route enabled must be a boolean")
      for label, value in (("int", 0), ("none", None), ("str", "false"))],
    ("route_signal_over_ceiling", _base,
     lambda w: setattr(_route(w), "signal_speed_km_s", 301), {"signal_speed_ceiling_km_s": 300},
     "route signaling exceeds established physical limit"),
    ("route_cargo_over_ceiling", _base,
     lambda w: setattr(_route(w), "cargo_speed_km_s", 101), {"cargo_speed_ceiling_km_s": 100},
     "route cargo transport exceeds established physical limit"),
    ("shipment_key_mismatch", _inflight,
     lambda w: w.in_transit.__setitem__("alias", _ship(w)), {},
     "invalid in-transit shipment"),
    ("shipment_route_absent", _inflight, lambda w: setattr(_ship(w), "route_id", "nowhere"), {},
     "invalid in-transit shipment"),
    ("shipment_destination_absent", _inflight,
     lambda w: setattr(_ship(w), "destination_id", "nowhere"), {},
     "invalid shipment destination or commodity"),
    ("shipment_energy_cargo", _inflight,
     lambda w: setattr(_ship(w), "cargo_name", "energy_j"), {},
     "invalid shipment destination or commodity"),
    ("shipment_amount_zero", _inflight, lambda w: setattr(_ship(w), "amount", 0), {},
     "shipment amount must be a positive integer"),
    ("shipment_due_negative", _inflight, lambda w: setattr(_ship(w), "arrives_s", -1), {},
     "shipment due must be a nonnegative integer"),
    ("capacity_key_empty", _inflight, lambda w: w.capacity_used.__setitem__("", 0), {},
     "invalid capacity key"),
    ("capacity_negative", _inflight,
     lambda w: w.capacity_used.__setitem__(next(iter(w.capacity_used)), -1), {},
     "capacity used must be a nonnegative integer"),
    ("pending_due_bool", _inflight, lambda w: setattr(w.pending[0], "due_s", True), {},
     "pending due must be a nonnegative integer"),
    ("pending_order_negative", _inflight, lambda w: setattr(w.pending[0], "order", -1), {},
     "pending order must be a nonnegative integer"),
    ("pending_in_past", _inflight,
     lambda w: (setattr(w, "time_s", 5), setattr(w.pending[0], "due_s", 4)), {},
     "scheduled event in the past"),
    ("pending_unknown_kind", _inflight, lambda w: setattr(w.pending[0], "kind", "bogus"), {},
     "unknown scheduled event"),
]


def _apply(*cases):
    """Build one world from the richest builder used, then apply each fault."""
    world = _inflight() if any(c[1] is _inflight for c in cases) else _base()
    profile_kwargs: dict = {}
    for _, _, mutate, kwargs, _ in cases:
        if mutate is not None:
            mutate(world)
        profile_kwargs.update(kwargs)
    return world, PhysicsProfile(**profile_kwargs)


def _outcome(world: Universe, profile: PhysicsProfile):
    try:
        world.validate(profile)
    except Exception as exc:  # noqa: BLE001 - characterizing the exact type
        return type(exc).__name__, str(exc)
    return None


class AcceptedStates(unittest.TestCase):
    def test_fixture_and_inflight_states_validate(self):
        for build in (_base, _inflight):
            with self.subTest(build=build.__name__):
                self.assertIsNone(build().validate(PhysicsProfile()))

    def test_inflight_builder_exercises_every_p0_section(self):
        w = _inflight()
        self.assertTrue(w.in_transit and w.capacity_used and w.heat_j > 0)
        self.assertEqual({e.kind for e in w.pending}, {"cargo_arrival", "report_arrival"})

    def test_validate_is_pure(self):
        for build in (_base, _inflight):
            w = build()
            before, digest = deepcopy(asdict(w)), w.digest()
            w.validate(PhysicsProfile())
            self.assertEqual((asdict(w), w.digest()), (before, digest))

    def test_boundary_values_are_accepted(self):
        accepted = [
            ({}, lambda w: None),
            ({"signal_speed_ceiling_km_s": LIGHT_KM_S,
              "cargo_speed_ceiling_km_s": LIGHT_KM_S}, lambda w: None),
            ({"signal_speed_ceiling_km_s": 300}, lambda w: None),  # route == ceiling
            ({}, lambda w: w.sites["frontier_port"].inventory.__setitem__("rations", 0)),
            ({}, lambda w: setattr(_route(w), "shipment_energy_j_per_unit_km", 0)),
            ({}, lambda w: setattr(_route(w), "signal_energy_j_per_km", 0)),
            ({}, lambda w: setattr(_route(w), "enabled", False)),
            ({}, lambda w: setattr(w.pending[0], "due_s", w.time_s)),
            # Pinned, not endorsed: arrival time is not cross-checked against
            # departure, route travel time, or the current clock in P0.
            ({}, lambda w: setattr(_ship(w), "arrives_s", 0)),
            # energy_j is a legal site inventory key (only cargo is barred).
            ({}, lambda w: w.sites["frontier_port"].inventory.__setitem__("energy_j", 0)),
        ]
        for i, (kwargs, mutate) in enumerate(accepted):
            with self.subTest(case=i):
                w = _inflight()
                mutate(w)
                self.assertIsNone(_outcome(w, PhysicsProfile(**kwargs)))


class RejectionSites(unittest.TestCase):
    def test_every_rejection_has_exact_type_and_message(self):
        for case in FAULTS:
            with self.subTest(case=case[0]):
                self.assertEqual(_outcome(*_apply(case)), ("ValueError", case[4]))

    def test_natural_rejects_bool_float_and_int_subclasses(self):
        class Int(int):
            pass

        for value in (True, False, 1.0, Int(1), None, "1"):
            with self.subTest(value=value):
                w = _base()
                w.time_s = value
                self.assertEqual(_outcome(w, PhysicsProfile()),
                                 ("ValueError", "time_s must be a nonnegative integer"))

    def test_pinned_non_valueerror_paths(self):
        """Pinned, not endorsed: malformed containers escape as non-ValueError.

        A later hardening change may convert these, but must do so deliberately
        and update this test; the split itself must not change them.
        """
        w = _base()
        w.sites["frontier_port"].inventory = None
        self.assertEqual(_outcome(w, PhysicsProfile())[0], "AttributeError")
        w = _base()
        w.actors["governor"].authorized_dispatch_sites = None
        self.assertEqual(_outcome(w, PhysicsProfile())[0], "TypeError")


class FirstFailureOrdering(unittest.TestCase):
    SECTION_ORDER = [
        "time_negative", "signal_ceiling_zero", "cargo_superluminal",
        "site_polity_empty", "actor_site_absent", "route_origin_absent",
        "shipment_route_absent", "capacity_key_empty", "pending_unknown_kind",
    ]

    def test_earlier_section_wins_for_every_pair(self):
        by_id = {c[0]: c for c in FAULTS}
        for a, b in itertools.combinations(self.SECTION_ORDER, 2):
            with self.subTest(first=a, second=b):
                self.assertEqual(_outcome(*_apply(by_id[a], by_id[b])),
                                 ("ValueError", by_id[a][4]))

    def test_within_section_order(self):
        cases = {c[0]: c for c in FAULTS}
        pairs = [
            ("time_negative", "heat_bool"), ("heat_bool", "serial_float"),
            ("signal_ceiling_zero", "cargo_ceiling_zero"),
            ("cargo_ceiling_zero", "signal_superluminal"),  # all natural() first
            ("signal_superluminal", "cargo_superluminal"),
            ("site_polity_empty", "commodity_empty"),
            ("actor_site_absent", "actor_auth_site_absent"),
            ("route_origin_absent", "route_distance_km_zero"),
            ("route_window_seconds_zero", "route_signal_energy_j_per_km_negative"),
            ("route_signal_energy_j_per_km_negative", "route_signal_over_ceiling"),
            ("shipment_destination_absent", "shipment_amount_zero"),
            ("shipment_amount_zero", "shipment_due_negative"),
            ("pending_due_bool", "pending_order_negative"),
        ]
        for a, b in pairs:
            with self.subTest(first=a, second=b):
                self.assertEqual(_outcome(*_apply(cases[a], cases[b])),
                                 ("ValueError", cases[a][4]))

    def test_mapping_insertion_order_decides_between_sites(self):
        w = _base()
        w.sites["union_depot"].polity_id = ""
        w.sites["frontier_port"].inventory[""] = 1
        self.assertEqual(_outcome(w, PhysicsProfile()), ("ValueError", "invalid site identity"))
        w = _base()
        w.sites["union_depot"].inventory[""] = 1
        w.sites["frontier_port"].polity_id = ""
        self.assertEqual(_outcome(w, PhysicsProfile()), ("ValueError", "empty commodity"))


class KernelTransaction(unittest.TestCase):
    def test_invalid_initial_state_is_refused(self):
        w = _base()
        w.time_s = -1
        with self.assertRaisesRegex(ValueError, "^time_s must be a nonnegative integer$"):
            CausalEngine(w)

    def test_rejected_commit_leaves_state_and_ledger_unchanged(self):
        engine = CausalEngine(fixture())
        before_digest, before_ledger = engine.state.digest(), list(engine.ledger)

        def zero_capacity(world):
            world.corridors["corridor_a"].capacity_units_per_window = 0
            return {}

        # A mutation with no kernel pre-checks, so the rejection comes from
        # validate() on the deep-copied candidate, not FeasibilityError.
        # (disrupt_route now refuses 0 up front; see test_gumas_unified_closure.)
        with self.assertRaises(ValueError) as caught:
            engine._commit("route_capacity_changed", None,
                           "fixture:invalid-capacity", zero_capacity)
        self.assertIs(type(caught.exception), ValueError)
        self.assertEqual(str(caught.exception),
                         "capacity_units_per_window must be a positive integer")
        self.assertEqual((engine.state.digest(), list(engine.ledger)),
                         (before_digest, before_ledger))


if __name__ == "__main__":
    unittest.main()
