"""P6 material shipment guards, separated from association authorization.

An institutional yes never creates cargo or changes physical access rights.
A completed mandate records exact departure and arrival coordinates so its
in-flight state remains verifiable even after the cargo receipt is processed.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .kernel import FeasibilityError, _travel_seconds
from .model import ScheduledEvent, Shipment

if TYPE_CHECKING:
    from .federated_model import Mandate
    from .kernel import CausalEngine
    from .model import Universe


def _valid_dispatch_clock(world: Universe, mandate: Mandate) -> int:
    """Check that dispatch followed approval and due time follows route physics."""
    departed, due = mandate.shipment_departed_s, mandate.shipment_due_s
    if type(departed) is not int or type(due) is not int:
        raise ValueError("executed mandate needs exact integer shipment times")
    if not mandate.authorized_at_s <= departed < mandate.expires_s:
        raise ValueError("executed mandate dispatch lies outside authority period")
    if departed > world.time_s:
        raise ValueError("executed mandate cannot dispatch in the future")
    route = world.corridors[mandate.cargo_route_id]
    expected = departed + _travel_seconds(route.distance_km,
                                           route.cargo_speed_km_s)
    if due != expected:
        raise ValueError("executed mandate has invalid cargo arrival time")
    return due


def _check_inflight_cargo(world: Universe, mandate: Mandate) -> None:
    """A pending P0 arrival must match every committed mandate cargo field."""
    shipment_id = mandate.shipment_id
    cargo = world.in_transit.get(shipment_id)
    if cargo is None:
        raise ValueError("undelivered mandate is missing in-transit cargo")
    route = world.corridors[mandate.cargo_route_id]
    fields = (
        cargo.route_id == mandate.cargo_route_id,
        cargo.cargo_name == mandate.commodity,
        cargo.amount == mandate.amount,
        cargo.sender_id == mandate.custodian_id,
        cargo.destination_id == route.destination_id,
        cargo.departed_s == mandate.shipment_departed_s,
        cargo.arrives_s == mandate.shipment_due_s,
    )
    if not all(fields):
        raise ValueError("in-transit cargo disagrees with authorized mandate")
    if not any(
        item.kind == "cargo_arrival"
        and item.due_s == mandate.shipment_due_s
        and item.payload.get("shipment_id") == shipment_id
        for item in world.pending
    ):
        raise ValueError("mandate shipment has no scheduled cargo receipt")


def validate_executed_shipment(world: Universe, mandate: Mandate) -> None:
    """Fail closed on ghost cargo, mismatched payloads and impossible times."""
    details = (mandate.shipment_id, mandate.shipment_departed_s,
               mandate.shipment_due_s)
    if mandate.status != "executed":
        if any(value is not None for value in details):
            raise ValueError("unexecuted mandate cannot claim shipment provenance")
        return
    shipment_id = mandate.shipment_id
    if not isinstance(shipment_id, str) or not shipment_id:
        raise ValueError("executed mandate requires an existing shipment reference")
    due = _valid_dispatch_clock(world, mandate)
    arriving_now = world.time_s == due and shipment_id in world.in_transit
    if world.time_s < due or arriving_now:
        _check_inflight_cargo(world, mandate)
    elif shipment_id in world.in_transit:
        raise ValueError("overdue mandate cargo remains incorrectly in transit")


def _available_cargo(world: Universe, mandate: Mandate, route) -> tuple[str, int]:
    window = world.time_s // route.window_seconds
    slot = f"{route.corridor_id}@{window}"
    occupied = world.capacity_used.get(slot, 0)
    if occupied + mandate.amount > route.capacity_units_per_window:
        raise FeasibilityError("federated shipment exceeds P0 physical capacity")
    source = world.sites[route.origin_id]
    if source.inventory.get(mandate.commodity, 0) < mandate.amount:
        raise FeasibilityError("mandate has no physical resource escrow or stock")
    energy = route.distance_km * mandate.amount * route.shipment_energy_j_per_unit_km
    if source.inventory.get("energy_j", 0) < energy:
        raise FeasibilityError("mandate execution lacks physical energy")
    return slot, energy


def dispatch_mandate_shipment(engine: CausalEngine, world: Universe,
                              mandate: Mandate, custodian_id: str) -> dict[str, Any]:
    """Commit one physically feasible shipment inside the P0 copy/commit txn."""
    route = engine._route(world, mandate.cargo_route_id)
    actor = world.actors[custodian_id]
    if actor.site_id != route.origin_id:
        raise FeasibilityError("custodian cannot physically access cargo source")
    slot, energy = _available_cargo(world, mandate, route)
    source = world.sites[route.origin_id]
    source.inventory[mandate.commodity] -= mandate.amount
    source.inventory["energy_j"] -= energy
    world.heat_j += energy
    world.capacity_used[slot] = world.capacity_used.get(slot, 0) + mandate.amount
    departure = world.time_s
    arrival = departure + _travel_seconds(route.distance_km, route.cargo_speed_km_s)
    shipment_id = engine._id(world, "shipment")
    world.in_transit[shipment_id] = Shipment(
        shipment_id, route.corridor_id, mandate.commodity, mandate.amount,
        custodian_id, route.destination_id, departure, arrival)
    event_id = engine._id(world, "scheduled")
    world.pending.append(ScheduledEvent(
        event_id, arrival, world.next_serial, "cargo_arrival",
        {"shipment_id": shipment_id}))
    mandate.status = "executed"
    mandate.shipment_id = shipment_id
    mandate.shipment_departed_s = departure
    mandate.shipment_due_s = arrival
    return {
        "shipment_id": shipment_id,
        "commodity": mandate.commodity,
        "amount": mandate.amount,
        "cargo_arrives_s": arrival,
        "energy_to_heat_j": energy,
        "association_approved": True,
        "site_dispatch_authorized":
            route.origin_id in actor.authorized_dispatch_sites,
        "authority": "synthetic_L2_only",
        "source_canon_promoted": False,
    }
