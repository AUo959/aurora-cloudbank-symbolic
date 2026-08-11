#!/usr/bin/env python3
"""Deterministic bounded tactical fleet resolver for GUMAS L2 fixtures.

This is an additive tactical harness. Numerical combat coefficients are scenario-local
proxies and must not be interpreted as CanonRec ship specifications.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

RESOLVER_ID = "GUMAS_TACTICAL_BATTLE_RESOLVER_v1"
RESOLVER_VERSION = "1.0.0"
DAMAGE_COEFFICIENT = 0.10
FIRE_INTERVAL_S = 30
EW_INTERVAL_S = 300
REPAIR_INTERVAL_S = 300
DECISION_INTERVAL_S = 300
DISENGAGEMENT_S = 1800


@dataclass
class Ship:
    side: str
    ship_id: str
    class_id: str
    shield: float
    hull: float
    max_shield: float
    max_hull: float
    base_power: float
    weapon_range_km: float
    stealth: float
    status: str = "undamaged"
    surrendered: bool = False
    destroyed: bool = False

    def hull_fraction(self) -> float:
        return max(0.0, self.hull / self.max_hull)

    def shield_fraction(self) -> float:
        return max(0.0, self.shield / self.max_shield)

    def combat_power(self) -> float:
        if self.destroyed or self.surrendered or self.status == "mission_kill":
            return 0.0
        return self.base_power * (0.35 + 0.65 * self.hull_fraction())


def _vadd(a: list[float], b: list[float]) -> list[float]:
    return [a[i] + b[i] for i in range(3)]


def _vsub(a: list[float], b: list[float]) -> list[float]:
    return [a[i] - b[i] for i in range(3)]


def _vscale(a: list[float], scalar: float) -> list[float]:
    return [value * scalar for value in a]


def _norm(a: list[float]) -> float:
    return math.sqrt(sum(value * value for value in a))


def _unit(a: list[float]) -> list[float]:
    magnitude = _norm(a)
    return [0.0, 0.0, 0.0] if magnitude == 0.0 else [value / magnitude for value in a]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def _canonical_sha256(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class TacticalBattle:
    def __init__(self, baseline: dict[str, Any], baseline_sha256: str):
        self.baseline = baseline
        self.baseline_sha256 = baseline_sha256
        self.seed = int(baseline["determinism"]["seed_u64"])
        self.rng = random.Random(self.seed)
        self.dt = int(baseline["battlefield"]["integration_step_s"])
        self.max_time = int(baseline["battlefield"]["max_run_duration_s"])
        self.boundary = float(baseline["battlefield"]["withdrawal_boundary_km"])
        self.axes = [
            float(baseline["battlefield"]["semi_axes_km"]["a"]),
            float(baseline["battlefield"]["semi_axes_km"]["b"]),
            float(baseline["battlefield"]["semi_axes_km"]["c"]),
        ]
        self.mu_km3_s2 = float(baseline["battlefield"]["gravitational_parameter_m3_s2"]) * 1e-9
        self.coefficients = baseline["fleet_template"]["class_coefficients"]
        self.composition = baseline["fleet_template"]["composition"]
        self.teams = {
            side: {officer["assignment"]: officer for officer in baseline["sides"][side]["command_team"]}
            for side in ("loyalist", "rebel")
        }
        self.ships = {side: self._instantiate(side) for side in ("loyalist", "rebel")}
        self.positions = {
            side: [float(v) for v in baseline["sides"][side]["initial_centroid_position_km"]]
            for side in self.ships
        }
        self.velocities = {
            side: [float(v) for v in baseline["sides"][side]["initial_centroid_velocity_km_s"]]
            for side in self.ships
        }
        self.initial_power = {
            side: sum(ship.base_power for ship in self.ships[side]) for side in self.ships
        }
        self.t = 0
        self.events: list[dict[str, Any]] = []
        self.withdraw = {side: False for side in self.ships}
        self.cease_offer = {side: False for side in self.ships}
        self.termination: str | None = None
        self.winner: str | None = None
        self.operational_outcome: str | None = None
        self.last_fire_t = 0
        self.ew_advantage = 0.0
        self.previous_separation = self._separation()

    def _instantiate(self, side: str) -> list[Ship]:
        ships: list[Ship] = []
        for item in self.composition:
            class_id = item["class_id"]
            prefix = class_id.replace("CLASS-", "").replace("-01", "")
            coeff = self.coefficients[class_id]
            for index in range(1, int(item["count"]) + 1):
                ships.append(
                    Ship(
                        side=side,
                        ship_id=f"{side[:3].upper()}-{prefix}-{index:02d}",
                        class_id=class_id,
                        shield=float(coeff["shield_units"]),
                        hull=float(coeff["hull_units"]),
                        max_shield=float(coeff["shield_units"]),
                        max_hull=float(coeff["hull_units"]),
                        base_power=float(coeff["combat_power"]),
                        weapon_range_km=float(coeff["effective_weapon_range_km"]),
                        stealth=float(coeff.get("stealth_factor", 0.0)),
                    )
                )
        return sorted(ships, key=lambda ship: ship.ship_id)

    def _officer_skill(self, side: str, role: str) -> float:
        return float(self.teams[side][role]["attributes"]["domain_skill"])

    def _commander(self, side: str, key: str) -> float:
        return float(self.teams[side]["commander"]["attributes"][key])

    def _separation(self) -> float:
        return _norm(_vsub(self.positions["loyalist"], self.positions["rebel"]))

    def _power(self, side: str) -> float:
        return sum(ship.combat_power() for ship in self.ships[side])

    def _power_fraction(self, side: str) -> float:
        return self._power(side) / self.initial_power[side]

    def _flagship(self, side: str) -> Ship:
        return next(ship for ship in self.ships[side] if ship.class_id == "CLASS-JUDICATOR-01")

    def _los_blocked(self) -> bool:
        p1 = self.positions["loyalist"]
        p2 = self.positions["rebel"]
        delta = _vsub(p2, p1)
        scaled_p = [p1[i] / self.axes[i] for i in range(3)]
        scaled_d = [delta[i] / self.axes[i] for i in range(3)]
        aa = _dot(scaled_d, scaled_d)
        bb = 2.0 * _dot(scaled_p, scaled_d)
        cc = _dot(scaled_p, scaled_p) - 1.0
        disc = bb * bb - 4.0 * aa * cc
        if aa == 0.0 or disc < 0.0:
            return False
        root = math.sqrt(disc)
        t1 = (-bb - root) / (2.0 * aa)
        t2 = (-bb + root) / (2.0 * aa)
        return (0.0 <= t1 <= 1.0) or (0.0 <= t2 <= 1.0)

    def _gravity(self, position: list[float]) -> list[float]:
        radius = _norm(position)
        if radius < 1e-9:
            return [0.0, 0.0, 0.0]
        return _vscale(position, -self.mu_km3_s2 / (radius ** 3))

    def _maneuver_acceleration(self, side: str) -> list[float]:
        enemy = "rebel" if side == "loyalist" else "loyalist"
        position = self.positions[side]
        delta = _vsub(self.positions[enemy], position)
        separation = _norm(delta)
        toward = _unit(delta)

        if self.withdraw[side]:
            outward = _unit(position)
            away = _vscale(toward, -1.0)
            direction = _unit(_vadd(_vscale(outward, 0.75), _vscale(away, 0.25)))
            magnitude = 0.006 * (0.8 + 0.4 * self._commander(side, "initiative"))
            return _vscale(direction, magnitude)

        desired_range = 2200.0 + (1.0 - self._commander(side, "aggression")) * 3600.0
        radial = _vscale(toward, 1.0 if separation > desired_range else -1.0)
        axis = [0.0, 0.0, 1.0] if side == "loyalist" else [0.35, 0.10, 0.93]
        tangential = _unit(_cross(axis, _unit(position)))
        flank = (
            0.10
            + 0.35
            * self._commander(side, "deception")
            * (1.0 - 0.45 * self._commander(side, "aggression"))
        )
        direction = _unit(_vadd(_vscale(radial, 1.0 - flank), _vscale(tangential, flank)))
        magnitude = 0.0025 + 0.0025 * self._commander(side, "initiative")
        magnitude *= 0.9 + 0.2 * self._officer_skill(side, "navigation")
        if _norm(position) < 450.0:
            direction = _unit(_vadd(_vscale(direction, 0.2), _vscale(_unit(position), 0.8)))
        return _vscale(direction, min(magnitude, 0.010))

    def _integrate(self) -> None:
        for side in ("loyalist", "rebel"):
            acceleration = _vadd(
                self._maneuver_acceleration(side),
                self._gravity(self.positions[side]),
            )
            self.velocities[side] = _vadd(
                self.velocities[side], _vscale(acceleration, self.dt)
            )
            self.positions[side] = _vadd(
                self.positions[side], _vscale(self.velocities[side], self.dt)
            )

    def _update_ew(self) -> None:
        loyalist = (
            0.62 * self._officer_skill("loyalist", "ew_sensors")
            + 0.20 * float(self.teams["loyalist"]["ew_sensors"]["attributes"]["initiative"])
            + 0.18 * self._commander("loyalist", "deception")
        )
        rebel = (
            0.62 * self._officer_skill("rebel", "ew_sensors")
            + 0.20 * float(self.teams["rebel"]["ew_sensors"]["attributes"]["initiative"])
            + 0.18 * self._commander("rebel", "deception")
        )
        jitter = (self.rng.random() - 0.5) * 0.04
        self.ew_advantage = max(-0.25, min(0.25, (loyalist - rebel) * 0.35 + jitter))
        self.events.append(
            {"t": self.t, "type": "ew_update", "loyalist_adv": round(self.ew_advantage, 4)}
        )

    def _target_candidates(self, target_side: str) -> tuple[list[Ship], list[float]]:
        candidates = [
            ship
            for ship in self.ships[target_side]
            if not ship.destroyed and not ship.surrendered and ship.status != "mission_kill"
        ]
        role_weight = {
            "CLASS-JUDICATOR-01": 1.80,
            "CLASS-AEGIS-01": 1.45,
            "CLASS-PALISADE-01": 1.25,
            "CLASS-SENTINEL-01": 0.90,
            "CLASS-OBSIDIAN-01": 0.65,
            "CLASS-VANGUARD-01": 1.00,
            "CLASS-PEREGRINE-01": 0.70,
            "CLASS-RELIANT-01": 0.85,
        }
        weights = []
        for ship in candidates:
            weight = role_weight[ship.class_id] * (1.0 - 0.55 * ship.stealth)
            weight *= 1.0 + 0.25 * (1.0 - ship.hull_fraction())
            weights.append(max(0.05, weight))
        return candidates, weights

    def _choose_target(self, target_side: str) -> Ship | None:
        candidates, weights = self._target_candidates(target_side)
        if not candidates:
            return None
        sample = self.rng.random() * sum(weights)
        running = 0.0
        for candidate, weight in zip(candidates, weights):
            running += weight
            if sample <= running:
                return candidate
        return candidates[-1]

    def _apply_damage(self, target: Ship, amount: float, attacker: Ship) -> None:
        if target.destroyed or target.surrendered:
            return
        previous_status = target.status
        absorbed = min(target.shield, amount)
        target.shield -= absorbed
        remainder = amount - absorbed
        if remainder > 0.0:
            target.hull = max(0.0, target.hull - remainder)

        hull_fraction = target.hull_fraction()
        if target.hull <= 0.0:
            target.destroyed = True
            target.status = "destroyed"
        elif hull_fraction < 0.20:
            target.status = "mission_kill"
        elif hull_fraction < 0.70:
            target.status = "damaged"

        if target.status != previous_status or remainder > 0.25:
            self.events.append(
                {
                    "t": self.t,
                    "type": "damage",
                    "attacker": attacker.ship_id,
                    "target": target.ship_id,
                    "damage": round(amount, 3),
                    "shield": round(target.shield, 3),
                    "hull": round(target.hull, 3),
                    "status": target.status,
                }
            )

    def _fire(self) -> bool:
        separation = self._separation()
        if self._los_blocked():
            return False
        fired = False

        for side in ("loyalist", "rebel"):
            enemy = "rebel" if side == "loyalist" else "loyalist"
            tactical = self._officer_skill(side, "tactical")
            coordination = self._commander(side, "command_skill")
            ew_factor = 1.0 + (self.ew_advantage if side == "loyalist" else -self.ew_advantage)

            for shooter in self.ships[side]:
                if shooter.destroyed or shooter.surrendered or shooter.status == "mission_kill":
                    continue
                if separation > shooter.weapon_range_km:
                    continue
                target = self._choose_target(enemy)
                if target is None:
                    continue

                detection = (
                    0.92
                    - 0.45 * target.stealth
                    + 0.12 * (self._officer_skill(side, "ew_sensors") - 0.80)
                )
                detection *= max(
                    0.55,
                    1.0 - separation / max(7000.0, shooter.weapon_range_km * 3.0) * 0.20,
                )
                if self.rng.random() > max(0.25, min(0.98, detection)):
                    continue

                range_factor = 0.30 + 0.70 * max(
                    0.0, 1.0 - separation / shooter.weapon_range_km
                )
                hull_factor = 0.35 + 0.65 * shooter.hull_fraction()
                noise = 0.88 + 0.24 * self.rng.random()
                damage = (
                    shooter.base_power
                    * DAMAGE_COEFFICIENT
                    * range_factor
                    * (0.70 + 0.30 * tactical)
                    * (0.80 + 0.20 * coordination)
                    * ew_factor
                    * hull_factor
                    * noise
                )
                if shooter.class_id == "CLASS-PALISADE-01":
                    damage *= 1.0 + float(
                        self.coefficients[shooter.class_id].get("carrier_projection", 0.0)
                    ) * self._officer_skill(side, "carrier_ops")
                self._apply_damage(target, damage, shooter)
                fired = True

        if fired:
            self.last_fire_t = self.t
        return fired

    def _repair(self) -> None:
        for side in ("loyalist", "rebel"):
            reliant = any(
                ship.class_id == "CLASS-RELIANT-01"
                and not ship.destroyed
                and ship.status != "mission_kill"
                for ship in self.ships[side]
            )
            palisade = any(
                ship.class_id == "CLASS-PALISADE-01"
                and not ship.destroyed
                and ship.status != "mission_kill"
                for ship in self.ships[side]
            )
            support = (0.12 if reliant else 0.0) + (0.05 if palisade else 0.0)
            if support <= 0.0:
                continue
            viable = [
                ship
                for ship in self.ships[side]
                if not ship.destroyed and ship.status != "mission_kill"
            ]
            if not viable:
                continue
            target = min(
                viable,
                key=lambda ship: ship.hull_fraction() + ship.shield_fraction(),
            )
            old_shield, old_hull = target.shield, target.hull
            target.shield = min(
                target.max_shield,
                target.shield
                + support * (0.5 + 0.5 * self._officer_skill(side, "logistics")),
            )
            if target.hull_fraction() > 0.25:
                target.hull = min(
                    target.max_hull,
                    target.hull
                    + support * 0.22 * self._officer_skill(side, "engineering"),
                )
            if target.shield > old_shield or target.hull > old_hull:
                self.events.append(
                    {
                        "t": self.t,
                        "type": "repair",
                        "side": side,
                        "target": target.ship_id,
                        "shield": round(target.shield, 3),
                        "hull": round(target.hull, 3),
                    }
                )

    def _decision_check(self) -> None:
        if self.t < 1200:
            return

        for side in ("loyalist", "rebel"):
            if self.withdraw[side]:
                continue
            fraction = self._power_fraction(side)
            threshold = (
                0.48
                + 0.28 * self._commander(side, "casualty_aversion")
                - 0.12 * self._commander(side, "aggression")
            )
            flagship = self._flagship(side)
            if flagship.destroyed or flagship.status == "mission_kill":
                threshold += 0.10
            if fraction < threshold:
                self.withdraw[side] = True
                self.events.append(
                    {
                        "t": self.t,
                        "type": "withdraw_order",
                        "side": side,
                        "power_fraction": round(fraction, 4),
                        "threshold": round(threshold, 4),
                    }
                )

        for side in ("loyalist", "rebel"):
            if self.cease_offer[side]:
                continue
            damage = 1.0 - self._power_fraction(side)
            if damage < 0.22:
                continue
            score = (
                self._commander(side, "negotiation_openness")
                + self._commander(side, "casualty_aversion")
                + damage
                + (0.12 if self.withdraw[side] else 0.0)
            )
            if score >= 1.30:
                self.cease_offer[side] = True
                self.events.append(
                    {"t": self.t, "type": "ceasefire_offer", "side": side, "score": round(score, 3)}
                )

        if all(self.cease_offer.values()):
            self.termination = "mutual_ceasefire"
            self.operational_outcome = "negotiated_stand_down"
            return

        for side in ("loyalist", "rebel"):
            fraction = self._power_fraction(side)
            flagship = self._flagship(side)
            if (
                fraction < 0.24
                and (flagship.destroyed or flagship.status == "mission_kill")
                and _norm(self.positions[side]) < self.boundary
            ):
                refuse = self._commander(side, "aggression") > 0.82 and fraction > 0.12
                if not refuse:
                    for ship in self.ships[side]:
                        if not ship.destroyed and ship.status != "mission_kill":
                            ship.surrendered = True
                            ship.status = "surrendered"
                    self.termination = "surrender"
                    self.winner = "rebel" if side == "loyalist" else "loyalist"
                    self.operational_outcome = f"{side}_surrender"
                    self.events.append(
                        {"t": self.t, "type": "surrender", "side": side, "power_fraction": round(fraction, 4)}
                    )
                    return

        for side in ("loyalist", "rebel"):
            if self.withdraw[side] and _norm(self.positions[side]) >= self.boundary:
                if self._separation() > self.previous_separation:
                    self.termination = "withdrawal"
                    if side == "rebel":
                        self.winner = "rebel"
                        self.operational_outcome = "rebel_breakout"
                    else:
                        self.winner = "rebel"
                        self.operational_outcome = "rebel_field_control"
                    self.events.append(
                        {
                            "t": self.t,
                            "type": "withdrawal_complete",
                            "side": side,
                            "radius_km": round(_norm(self.positions[side]), 1),
                        }
                    )
                    return

        for side in ("loyalist", "rebel"):
            if self._power(side) <= 1e-9:
                self.termination = "combat_incapacity"
                self.winner = "rebel" if side == "loyalist" else "loyalist"
                self.operational_outcome = f"{side}_combat_incapacity"
                return

        if (
            self.t - self.last_fire_t >= DISENGAGEMENT_S
            and self._separation() > self.previous_separation
            and self.t > 2400
        ):
            self.termination = "mutual_disengagement"
            if self._power_fraction("rebel") > 0.45:
                self.winner = "rebel"
                self.operational_outcome = "rebel_breakout"
            else:
                self.operational_outcome = "unresolved_disengagement"

    def _check_collision(self) -> None:
        for side in ("loyalist", "rebel"):
            x, y, z = self.positions[side]
            ellipsoid_value = (
                (x / self.axes[0]) ** 2
                + (y / self.axes[1]) ** 2
                + (z / self.axes[2]) ** 2
            )
            if ellipsoid_value <= 1.0:
                self.termination = "formation_collision"
                self.winner = "rebel" if side == "loyalist" else "loyalist"
                self.operational_outcome = f"{side}_formation_collision"
                self.events.append({"t": self.t, "type": "formation_collision", "side": side})
                return

    def run(self) -> dict[str, Any]:
        self._update_ew()
        while self.t < self.max_time and self.termination is None:
            self._integrate()
            self.t += self.dt

            if self.t % EW_INTERVAL_S == 0:
                self._update_ew()
            if self.t % FIRE_INTERVAL_S == 0:
                self._fire()
            if self.t % REPAIR_INTERVAL_S == 0:
                self._repair()
            if self.t % DECISION_INTERVAL_S == 0:
                self._decision_check()
            if self.termination is None:
                self._check_collision()

            self.previous_separation = self._separation()

        if self.termination is None:
            self.termination = "hard_time_limit"
            self.operational_outcome = "stalemate"

        result = self._summary()
        result["final_state_sha256"] = _canonical_sha256(result)
        return result

    def _summary(self) -> dict[str, Any]:
        sides: dict[str, Any] = {}
        for side in ("loyalist", "rebel"):
            counts: dict[str, int] = {}
            ships: dict[str, Any] = {}
            for ship in self.ships[side]:
                counts[ship.status] = counts.get(ship.status, 0) + 1
                ships[ship.ship_id] = {
                    "class_id": ship.class_id,
                    "status": ship.status,
                    "shield": round(ship.shield, 3),
                    "hull": round(ship.hull, 3),
                }
            sides[side] = {
                "remaining_power": round(self._power(side), 3),
                "remaining_power_fraction": round(self._power_fraction(side), 4),
                "states_count": counts,
                "radius_km": round(_norm(self.positions[side]), 1),
                "position_km": [round(value, 1) for value in self.positions[side]],
                "velocity_km_s": [round(value, 3) for value in self.velocities[side]],
                "ships": ships,
            }

        return {
            "resolver_id": RESOLVER_ID,
            "resolver_version": RESOLVER_VERSION,
            "baseline_id": self.baseline["baseline_id"],
            "baseline_sha256": self.baseline_sha256,
            "seed_u64": self.seed,
            "historical_canon_status": "non_canon_simulation_instance",
            "termination": self.termination,
            "operational_outcome": self.operational_outcome,
            "winner": self.winner,
            "elapsed_s": self.t,
            "separation_km": round(self._separation(), 1),
            "sides": sides,
            "events": self.events,
        }


def load_baseline(path: str | Path) -> tuple[dict[str, Any], str]:
    baseline = json.loads(Path(path).read_text(encoding="utf-8"))
    return baseline, _canonical_sha256(baseline)


def run_baseline(path: str | Path) -> dict[str, Any]:
    baseline, digest = load_baseline(path)
    return TacticalBattle(baseline, digest).run()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", help="Path to tactical battle baseline JSON")
    parser.add_argument("--output", help="Optional result JSON path")
    args = parser.parse_args()
    result = run_baseline(args.baseline)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
