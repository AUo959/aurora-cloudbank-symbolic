"""Small, explicit, integer-unit L2 world model for GUMAS Unified P0.

All state is synthetic fixture state until an independently authorized source
adapter is connected. No CanonRec import, L1 handle, or external I/O occurs.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from typing import Any


@dataclass(frozen=True)
class PhysicsProfile:
    # Baseline sublight profile only. Canonical FTL requires a separate,
    # provenance-bound rule profile; never silently exceed this speed.
    signal_speed_ceiling_km_s: int = 299792
    cargo_speed_ceiling_km_s: int = 50000


@dataclass
class Site:
    site_id: str
    polity_id: str
    inventory: dict[str, int]


@dataclass
class Actor:
    actor_id: str
    site_id: str
    # Institutional permission is distinct from physical feasibility.
    authorized_dispatch_sites: tuple[str, ...] = ()
    received_reports: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Corridor:
    corridor_id: str
    origin_id: str
    destination_id: str
    distance_km: int
    cargo_speed_km_s: int
    signal_speed_km_s: int
    capacity_units_per_window: int
    window_seconds: int
    shipment_energy_j_per_unit_km: int = 1
    signal_energy_j_per_km: int = 1
    enabled: bool = True


@dataclass
class Shipment:
    shipment_id: str
    route_id: str
    cargo_name: str
    amount: int
    sender_id: str
    destination_id: str
    departed_s: int
    arrives_s: int


@dataclass
class ScheduledEvent:
    scheduled_id: str
    due_s: int
    order: int
    kind: str
    payload: dict[str, Any]


P0_SCHEDULED_EVENT_KINDS = ("cargo_arrival", "report_arrival")


def _natural(value: int, name: str, *, positive: bool = False) -> None:
    if type(value) is not int or value < (1 if positive else 0):
        raise ValueError(f"{name} must be a nonnegative integer" if not positive
                         else f"{name} must be a positive integer")


def _validate_scalars(world: Any) -> None:
    _natural(world.time_s, "time_s")
    _natural(world.heat_j, "heat_j")
    _natural(world.next_serial, "next_serial")


def _validate_profile(profile: PhysicsProfile) -> None:
    _natural(profile.signal_speed_ceiling_km_s, "signal ceiling", positive=True)
    _natural(profile.cargo_speed_ceiling_km_s, "cargo ceiling", positive=True)
    if profile.signal_speed_ceiling_km_s > 299792:
        raise ValueError("P0 does not authorize superluminal signaling")
    if profile.cargo_speed_ceiling_km_s > 299792:
        raise ValueError("P0 does not authorize superluminal cargo transport")


def _validate_sites(world: Any) -> None:
    for key, site in world.sites.items():
        if key != site.site_id or not site.polity_id:
            raise ValueError("invalid site identity")
        for name, amount in site.inventory.items():
            if not name:
                raise ValueError("empty commodity")
            _natural(amount, f"inventory {key}/{name}")


def _validate_actors(world: Any) -> None:
    for key, actor in world.actors.items():
        if key != actor.actor_id or actor.site_id not in world.sites:
            raise ValueError("invalid actor identity or site")
        if any(s not in world.sites for s in actor.authorized_dispatch_sites):
            raise ValueError("invalid actor authorization site")


def _validate_corridor(world: Any, key: str, route: Any, profile: PhysicsProfile) -> None:
    if key != route.corridor_id:
        raise ValueError("invalid route identity")
    if route.origin_id not in world.sites or route.destination_id not in world.sites:
        raise ValueError("route endpoint absent")
    for n in ("distance_km", "cargo_speed_km_s", "signal_speed_km_s",
              "capacity_units_per_window", "window_seconds"):
        _natural(getattr(route, n), n, positive=True)
    for n in ("shipment_energy_j_per_unit_km", "signal_energy_j_per_km"):
        _natural(getattr(route, n), n)
    if route.signal_speed_km_s > profile.signal_speed_ceiling_km_s:
        raise ValueError("route signaling exceeds established physical limit")
    if route.cargo_speed_km_s > profile.cargo_speed_ceiling_km_s:
        raise ValueError("route cargo transport exceeds established physical limit")


def _validate_corridors(world: Any, profile: PhysicsProfile) -> None:
    for key, route in world.corridors.items():
        _validate_corridor(world, key, route, profile)


def _validate_in_transit(world: Any) -> None:
    for key, shipment in world.in_transit.items():
        if key != shipment.shipment_id or shipment.route_id not in world.corridors:
            raise ValueError("invalid in-transit shipment")
        if shipment.destination_id not in world.sites or shipment.cargo_name == "energy_j":
            raise ValueError("invalid shipment destination or commodity")
        _natural(shipment.amount, "shipment amount", positive=True)
        _natural(shipment.arrives_s, "shipment due")


def _validate_capacity(world: Any) -> None:
    for k, used in world.capacity_used.items():
        if not k:
            raise ValueError("invalid capacity key")
        _natural(used, "capacity used")


def _validate_pending(world: Any) -> None:
    for event in world.pending:
        _natural(event.due_s, "pending due")
        _natural(event.order, "pending order")
        if event.due_s < world.time_s:
            raise ValueError("scheduled event in the past")
        if event.kind not in P0_SCHEDULED_EVENT_KINDS:
            raise ValueError("unknown scheduled event")


@dataclass
class Universe:
    time_s: int
    sites: dict[str, Site]
    actors: dict[str, Actor]
    corridors: dict[str, Corridor]
    in_transit: dict[str, Shipment] = field(default_factory=dict)
    pending: list[ScheduledEvent] = field(default_factory=list)
    capacity_used: dict[str, int] = field(default_factory=dict)
    heat_j: int = 0
    next_serial: int = 0

    def validate(self, profile: PhysicsProfile) -> None:
        # Order is part of the contract: the first failing section's error is
        # the transaction's rejection reason. Later layers insert sections at
        # the seams noted below without reordering existing calls.
        _validate_scalars(self)
        _validate_profile(profile)
        _validate_sites(self)
        _validate_actors(self)
        # Seam: identity, institution and motion sections follow actors.
        _validate_corridors(self, profile)
        _validate_in_transit(self)
        # Seam: remote ballot section follows in-transit shipments.
        _validate_capacity(self)
        _validate_pending(self)

    def totals(self) -> dict[str, int]:
        """Account for all represented matter and energy, including in-flight cargo.

        Consumed useful energy is counted as heat, NOT destroyed. Nothing here
        implies social/political scores are physically conserved quantities.
        """
        totals: dict[str, int] = {}
        for site in self.sites.values():
            for commodity, amount in site.inventory.items():
                totals[commodity] = totals.get(commodity, 0) + amount
        for shipment in self.in_transit.values():
            key = shipment.cargo_name
            totals[key] = totals.get(key, 0) + shipment.amount
        totals["energy_j"] = totals.get("energy_j", 0) + self.heat_j
        return {k: v for k, v in totals.items() if v != 0}

    def digest(self) -> str:
        data = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
        return hashlib.sha256(data).hexdigest()
