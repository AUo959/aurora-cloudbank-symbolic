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
    identity_bindings: dict[str, dict[str, Any]] = field(default_factory=dict)

    def validate(self, profile: PhysicsProfile) -> None:
        def natural(value: int, name: str, *, positive: bool = False) -> None:
            if type(value) is not int or value < (1 if positive else 0):
                raise ValueError(f"{name} must be a nonnegative integer" if not positive
                                 else f"{name} must be a positive integer")

        natural(self.time_s, "time_s")
        natural(self.heat_j, "heat_j")
        natural(self.next_serial, "next_serial")
        natural(profile.signal_speed_ceiling_km_s, "signal ceiling", positive=True)
        natural(profile.cargo_speed_ceiling_km_s, "cargo ceiling", positive=True)
        if profile.signal_speed_ceiling_km_s > 299792:
            raise ValueError("P0 does not authorize superluminal signaling")
        if profile.cargo_speed_ceiling_km_s > 299792:
            raise ValueError("P0 does not authorize superluminal cargo transport")
        for key, site in self.sites.items():
            if key != site.site_id or not site.polity_id:
                raise ValueError("invalid site identity")
            for name, amount in site.inventory.items():
                if not name:
                    raise ValueError("empty commodity")
                natural(amount, f"inventory {key}/{name}")
        for key, actor in self.actors.items():
            if key != actor.actor_id or actor.site_id not in self.sites:
                raise ValueError("invalid actor identity or site")
            if any(s not in self.sites for s in actor.authorized_dispatch_sites):
                raise ValueError("invalid actor authorization site")
        bound_entities: set[tuple[str, str]] = set()
        for actor_id, record in self.identity_bindings.items():
            if not isinstance(record, dict):
                raise ValueError("identity binding must be an object")
            if (actor_id not in self.actors or record.get("actor_id") != actor_id
                    or record.get("schema") != "gumas.unified.fixture_identity_binding.p2"
                    or record.get("scope") != "synthetic_fixture_only"
                    or record.get("grant_authenticated") is not False
                    or record.get("source_canon_promoted") is not False
                    or record.get("actor_permissions_changed") is not False
                    or record.get("agent_memory_injected") is not False):
                raise ValueError("unauthorized or inconsistent L2 fixture identity binding")
            key = (record.get("world_id"), record.get("entity_id"))
            if not all(isinstance(value, str) and value for value in key):
                raise ValueError("invalid identity reference")
            if key in bound_entities:
                raise ValueError("duplicate ACE identity binding")
            bound_entities.add(key)
            natural(record.get("bound_at_s"), "identity bound_at_s")
            natural(record.get("valid_until_s"), "identity valid_until_s")
            if (record["bound_at_s"] > self.time_s
                    or record["valid_until_s"] <= record["bound_at_s"]):
                raise ValueError("identity binding has invalid validity interval")
            payload = {k: v for k, v in record.items() if k != "binding_sha256"}
            expected = hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
            ).hexdigest()
            if record.get("binding_sha256") != expected:
                raise ValueError("identity binding fingerprint does not match record")
        for key, route in self.corridors.items():
            if key != route.corridor_id:
                raise ValueError("invalid route identity")
            if route.origin_id not in self.sites or route.destination_id not in self.sites:
                raise ValueError("route endpoint absent")
            for n in ("distance_km", "cargo_speed_km_s", "signal_speed_km_s",
                      "capacity_units_per_window", "window_seconds"):
                natural(getattr(route, n), n, positive=True)
            for n in ("shipment_energy_j_per_unit_km", "signal_energy_j_per_km"):
                natural(getattr(route, n), n)
            if route.signal_speed_km_s > profile.signal_speed_ceiling_km_s:
                raise ValueError("route signaling exceeds established physical limit")
            if route.cargo_speed_km_s > profile.cargo_speed_ceiling_km_s:
                raise ValueError("route cargo transport exceeds established physical limit")
        for key, shipment in self.in_transit.items():
            if key != shipment.shipment_id or shipment.route_id not in self.corridors:
                raise ValueError("invalid in-transit shipment")
            if shipment.destination_id not in self.sites or shipment.cargo_name == "energy_j":
                raise ValueError("invalid shipment destination or commodity")
            natural(shipment.amount, "shipment amount", positive=True)
            natural(shipment.arrives_s, "shipment due")
        for k, used in self.capacity_used.items():
            if not k:
                raise ValueError("invalid capacity key")
            natural(used, "capacity used")
        for event in self.pending:
            natural(event.due_s, "pending due")
            natural(event.order, "pending order")
            if event.due_s < self.time_s:
                raise ValueError("scheduled event in the past")
            if event.kind not in ("cargo_arrival", "report_arrival"):
                raise ValueError("unknown scheduled event")

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
        payload = asdict(self)
        # Empty P2 identity storage is not a new fact: preserve exact P0/P1
        # state hashes and existing historical replay receipts.
        if not payload["identity_bindings"]:
            payload.pop("identity_bindings")
        data = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
        return hashlib.sha256(data).hexdigest()
