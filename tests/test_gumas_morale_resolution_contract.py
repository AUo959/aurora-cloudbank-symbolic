from __future__ import annotations

import copy
import inspect

import pytest

from simulation.runtime.gumas_morale_resolution import Phase8Error
from simulation.runtime.gumas_morale_resolution.constants import (
    CEASEFIRE_OFFER_TTL_MACROSTEPS,
    HARD_LIMIT_MS,
    WITHDRAWAL_BOUNDARY_UM,
)
from simulation.runtime.gumas_morale_resolution import kernel as phase8_kernel
from simulation.runtime.gumas_morale_resolution.test_support import (
    commands,
    damage,
    phase7_receipt,
    run,
    state,
    vessel,
)
from simulation.runtime.gumas_movement_geometry.kernel import (
    _hash_without_field as state_hash,
)

pytestmark = pytest.mark.unit


def _ship(snapshot, ship_id):
    return next(item for item in snapshot["vessels"] if item["ship_id"] == ship_id)


def _next_phase7_state(*, macrostep, elapsed, vessels=None):
    return state(macrostep=macrostep, elapsed=elapsed, vessels=vessels)


def test_ceasefire_offer_expiry_is_exact_and_negotiation_signal_tracks_opponent():
    first = state(macrostep=5)
    _, r1, _ = run(
        first,
        phase7_receipt(first),
        commands(lp="CEASEFIRE_PROBE", rp="HOLD"),
    )
    expiry = r1["ceasefire_offer_expiry_macrostep_by_side"]["loyalist"]
    assert expiry == 5 + CEASEFIRE_OFFER_TTL_MACROSTEPS
    assert r1["negotiation_signal_q1000_by_side"] == {
        "loyalist": 0,
        "rebel": 1000,
    }

    at_expiry = _next_phase7_state(macrostep=expiry, elapsed=expiry * 10_000)
    _, r_expiry, _ = run(
        at_expiry,
        phase7_receipt(at_expiry),
        commands(),
        r1,
    )
    assert r_expiry["active_ceasefire_offer_by_side"]["loyalist"] is True

    after_expiry = _next_phase7_state(
        macrostep=expiry + 1,
        elapsed=(expiry + 1) * 10_000,
    )
    _, r_after, _ = run(
        after_expiry,
        phase7_receipt(after_expiry),
        commands(),
        r_expiry,
    )
    assert r_after["active_ceasefire_offer_by_side"]["loyalist"] is False
    assert r_after["negotiation_signal_q1000_by_side"]["rebel"] == 0


def test_greater_fleet_hull_loss_and_new_incapacity_cannot_improve_side_morale_or_cohesion():
    base_vessels = [
        vessel("L1", "loyalist", "F-L"),
        vessel("L2", "loyalist", "F-L"),
        vessel("R1", "rebel", "F-R"),
        vessel("R2", "rebel", "F-R"),
    ]

    low_vessels = copy.deepcopy(base_vessels)
    _ship({"vessels": low_vessels}, "L2")["physical"]["hull_current_milliunits"] = 900
    low = state(vessels=low_vessels)
    low_receipt = phase7_receipt(
        low,
        [damage("L2", hull_loss=100)],
        effect_count=1,
    )
    low_next, _, _ = run(low, low_receipt, commands())

    high_vessels = copy.deepcopy(base_vessels)
    high_l2 = _ship({"vessels": high_vessels}, "L2")
    high_l2["physical"]["hull_current_milliunits"] = 500
    high_l2["disposition"] = "disabled"
    high = state(vessels=high_vessels)
    high_receipt = phase7_receipt(
        high,
        [
            damage(
                "L2",
                hull_loss=500,
                before="combat_capable",
                after="disabled",
            )
        ],
        effect_count=1,
    )
    high_next, _, _ = run(high, high_receipt, commands())

    assert _ship(high_next, "L1")["morale_q1000"] <= _ship(low_next, "L1")["morale_q1000"]
    assert _ship(high_next, "L1")["cohesion_q1000"] <= _ship(low_next, "L1")["cohesion_q1000"]


def test_exact_seven_tenths_withdrawal_threshold_and_no_intent_case():
    boundary = WITHDRAWAL_BOUNDARY_UM
    loyal = [vessel("L00", "loyalist", "F-L")]
    rebel = []
    for index in range(10):
        if index < 7:
            position = [boundary + index, 0, 0]
            velocity = [1, 0, 0]
        else:
            position = [1_000_000_000_000 + index, 0, 0]
            velocity = [0, 0, 0]
        rebel.append(
            vessel(
                f"R{index:02d}",
                "rebel",
                "F-R",
                position=position,
                velocity=velocity,
            )
        )
    snapshot = state(vessels=loyal + rebel)
    _, resolution, receipt = run(
        snapshot,
        phase7_receipt(snapshot),
        commands(rp="DISENGAGE"),
    )
    withdrawal = resolution["withdrawal_by_side"]["rebel"]
    assert withdrawal["withdrawn_mobile_fraction_q1000"] == 700
    assert withdrawal["success"] is True
    assert receipt["terminal_outcome"]["termination_mode"] == "successful_withdrawal"
    assert receipt["terminal_outcome"]["victor_side_id"] is None

    _, no_intent, no_intent_receipt = run(
        snapshot,
        phase7_receipt(snapshot),
        commands(),
    )
    assert no_intent["withdrawal_by_side"]["rebel"]["success"] is False
    assert no_intent_receipt["terminal_outcome"]["termination_mode"] == "ongoing"


def test_surrender_pressure_unmet_and_simultaneous_bilateral_predicates():
    healthy = state()
    _, healthy_resolution, healthy_receipt = run(
        healthy,
        phase7_receipt(healthy),
        commands(lp="CEASEFIRE_PROBE"),
    )
    assert healthy_resolution["surrender_by_side"]["loyalist"]["predicate"] is False
    assert healthy_receipt["terminal_outcome"]["termination_mode"] == "ongoing"

    vessels = [
        vessel("L1", "loyalist", "F-L", disposition="degraded", hull=300, morale=100, cohesion=100, weapons=200),
        vessel("L2", "loyalist", "F-L", disposition="disabled", hull=100, morale=100, cohesion=100, propulsion=100, weapons=100),
        vessel("R1", "rebel", "F-R", disposition="degraded", hull=300, morale=100, cohesion=100, weapons=200),
        vessel("R2", "rebel", "F-R", disposition="disabled", hull=100, morale=100, cohesion=100, propulsion=100, weapons=100),
    ]
    pressured = state(vessels=vessels)
    bilateral = commands(
        lp="DISENGAGE",
        rp="DISENGAGE",
        resolve="low",
        withdrawal_viability=0,
    )
    _, resolution, receipt = run(
        pressured,
        phase7_receipt(pressured, effect_count=1),
        bilateral,
    )
    assert resolution["surrender_by_side"]["loyalist"]["predicate"] is True
    assert resolution["surrender_by_side"]["rebel"]["predicate"] is True
    assert receipt["terminal_outcome"]["termination_mode"] == "mutual_stand_down"
    assert receipt["terminal_outcome"]["victor_side_id"] is None
    assert resolution["protected_ship_ids"] == sorted(
        resolution["protected_ship_ids"]
    )
    assert set(resolution["protected_ship_ids"]) == {"L1", "L2", "R1", "R2"}


def test_mutual_incapacity_mutual_annihilation_and_terminal_precedence_at_hard_limit():
    mutual_incap = state(
        elapsed=HARD_LIMIT_MS,
        vessels=[
            vessel("L1", "loyalist", "F-L", disposition="disabled", hull=100, propulsion=100, weapons=100),
            vessel("R1", "rebel", "F-R", disposition="disabled", hull=100, propulsion=100, weapons=100),
        ],
    )
    _, incap_resolution, incap_receipt = run(
        mutual_incap,
        phase7_receipt(mutual_incap),
        commands(),
    )
    assert incap_receipt["terminal_outcome"]["termination_mode"] == "mutual_incapacity"
    assert incap_receipt["terminal_outcome"]["victor_side_id"] is None
    assert set(incap_resolution["protected_ship_ids"]) == {"L1", "R1"}

    mutual_ann = state(
        elapsed=HARD_LIMIT_MS,
        vessels=[
            vessel("L1", "loyalist", "F-L", disposition="destroyed", hull=0, morale=0, cohesion=0, propulsion=0, weapons=0),
            vessel("R1", "rebel", "F-R", disposition="destroyed", hull=0, morale=0, cohesion=0, propulsion=0, weapons=0),
        ],
    )
    _, _, ann_receipt = run(
        mutual_ann,
        phase7_receipt(mutual_ann),
        commands(),
    )
    assert ann_receipt["terminal_outcome"]["termination_mode"] == "mutual_annihilation"
    assert ann_receipt["terminal_outcome"]["victor_side_id"] is None
    assert ann_receipt["terminal_outcome"]["stalemate"] is False


def test_public_boundary_rejects_untrusted_upstream_shapes_and_command_authority():
    bad_disposition = state()
    bad_disposition["vessels"][0]["disposition"] = "mystery_state"
    bad_disposition["state_sha256"] = state_hash(
        bad_disposition, "state_sha256"
    )
    with pytest.raises(Phase8Error):
        run(bad_disposition, phase7_receipt(bad_disposition), commands())

    foreign = state()
    foreign_receipt = phase7_receipt(
        foreign,
        [damage("NOT-A-SHIP", hull_loss=100)],
        effect_count=1,
    )
    with pytest.raises(Phase8Error):
        run(foreign, foreign_receipt, commands())

    prose_commands = commands()
    prose_commands["F-L"]["prose_inputs_used"] = True
    from simulation.runtime.gumas_command_policy import policy as cp

    prose_commands["F-L"]["decision_sha256"] = cp.sha256_canonical(
        {k: v for k, v in prose_commands["F-L"].items() if k != "decision_sha256"}
    )
    with pytest.raises(Phase8Error):
        run(state(), phase7_receipt(state()), prose_commands)


def test_boundary_and_composite_source_identity_are_bound_into_output_and_prior_state():
    snapshot = state()
    next_state, resolution, receipt = run(
        snapshot,
        phase7_receipt(snapshot),
        commands(),
    )
    assert receipt["phase8_public_boundary_validated"] is True
    assert receipt["phase8_boundary_source_identity"] == resolution[
        "phase8_boundary_source_identity"
    ]
    assert receipt["phase8_composite_source_sha256"] == resolution[
        "phase8_composite_source_sha256"
    ]
    assert next_state["phase8_composite_source_sha256"] == receipt[
        "phase8_composite_source_sha256"
    ]
    assert next_state["last_phase8_resolution_state_sha256"] == resolution[
        "resolution_state_sha256"
    ]

    bad_prior = copy.deepcopy(resolution)
    bad_prior["phase8_composite_source_sha256"] = "0" * 64
    bad_prior["resolution_state_sha256"] = phase8_kernel._hash_without_field(
        bad_prior, "resolution_state_sha256"
    )
    next_snapshot = _next_phase7_state(macrostep=11, elapsed=110_000)
    with pytest.raises(Phase8Error):
        run(
            next_snapshot,
            phase7_receipt(next_snapshot),
            commands(),
            bad_prior,
        )


def test_phase9_consumable_control_fields_and_no_forbidden_authority_in_core():
    snapshot = state()
    _, resolution, receipt = run(
        snapshot,
        phase7_receipt(snapshot),
        commands(lp="CEASEFIRE_PROBE"),
    )
    for field in (
        "negotiation_signal_q1000_by_side",
        "protected_ship_ids",
        "engagement_status_by_side",
        "terminal_outcome",
    ):
        assert field in resolution
    assert receipt["ambient_rng_used"] is False
    assert receipt["floating_authority_used"] is False
    assert receipt["prose_inputs_used"] is False

    source = inspect.getsource(phase8_kernel)
    assert "import random" not in source
    assert "canonrec_class_id" not in source
    assert "baseline_class_id" not in source
    assert "organization_id" not in source
