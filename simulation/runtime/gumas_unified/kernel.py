"""Transactional, reproducible and information-local causal engine: P0.

One kernel-owned authoritative state per isolated L2 instance. All writes use
a validated copy-and-commit transition. Event receipts are SHA256 chained and
have no wall-clock timestamps, ambient randomness, network calls or L1 writes.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import hashlib
import json
from typing import TYPE_CHECKING, Any, Callable

from .federated_model import MandateRequest
from .model import Corridor, PhysicsProfile, ScheduledEvent, Shipment, Universe

if TYPE_CHECKING:
    from .political_actions import ReliefProposal


class FeasibilityError(ValueError):
    """A proposed action is not feasible in the currently established field."""


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def _travel_seconds(distance_km: int, speed_km_s: int) -> int:
    return (distance_km + speed_km_s - 1) // speed_km_s


@dataclass(frozen=True)
class Receipt:
    number: int
    time_s: int
    kind: str
    actor_id: str | None
    cause: str
    effect: dict[str, Any]
    before: str
    after: str
    previous: str
    digest: str

    def payload(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if k != "digest"}


def verify_ledger(ledger: list[Receipt], initial_state_hash: str,
                  final_state_hash: str) -> bool:
    """Verify receipt linkage and final hash, not full historical re-execution."""
    prev = "GENESIS"
    state_hash = initial_state_hash
    for number, receipt in enumerate(ledger, 1):
        if (receipt.number != number or receipt.previous != prev
                or receipt.before != state_hash
                or receipt.digest != _digest(receipt.payload())):
            return False
        prev, state_hash = receipt.digest, receipt.after
    return state_hash == final_state_hash


class CausalEngine:
    def __init__(self, initial: Universe, profile: PhysicsProfile | None = None,
                 *, run_id: str = "synthetic-p0") -> None:
        self.profile = profile or PhysicsProfile()
        self._state = deepcopy(initial)
        self._state.validate(self.profile)
        if not run_id or not run_id.startswith("synthetic-"):
            raise ValueError("P0 runs must be explicitly labeled synthetic")
        self.run_id = run_id
        self.initial_hash = self._state.digest()
        self._initial_totals = self._state.totals()
        self._ledger: list[Receipt] = []

    @property
    def state(self) -> Universe:
        """Return a snapshot; external callers cannot mutate committed L2 state."""
        return deepcopy(self._state)

    @property
    def ledger(self) -> list[Receipt]:
        """Return receipts by value; callers cannot rewrite recorded history."""
        return deepcopy(self._ledger)

    def _commit(self, kind: str, actor: str | None, cause: str,
                mutation: Callable[[Universe], dict[str, Any]]) -> Receipt:
        if not cause:
            raise ValueError("a transition requires a causal reference")
        before = self._state.digest()
        candidate = deepcopy(self._state)
        effect = mutation(candidate)
        candidate.validate(self.profile)
        if candidate.totals() != self._initial_totals:
            raise AssertionError("closed-system resource and energy accounting failed")
        after = candidate.digest()
        previous = self._ledger[-1].digest if self._ledger else "GENESIS"
        receipt = Receipt(number=len(self._ledger) + 1, time_s=candidate.time_s,
                          kind=kind, actor_id=actor, cause=cause,
                          effect=effect, before=before, after=after,
                          previous=previous, digest="")
        receipt = Receipt(**{**receipt.payload(), "digest": _digest(receipt.payload())})
        self._state = candidate
        self._ledger.append(receipt)
        return deepcopy(receipt)

    def bind_fixture_identity(self, ace_projection: dict[str, Any],
                              grant: dict[str, Any]) -> Receipt:
        """Commit a provenance-labeled synthetic identity alias, not source canon.

        A fixture-only grant is explicit test intent, not authenticated
        operator authorization. No ACE or tactical processes are invoked.
        """
        from .bindings import prepare_fixture_identity_binding

        record = prepare_fixture_identity_binding(self, ace_projection, grant)

        def change(world: Universe) -> dict[str, Any]:
            actor_id = record["actor_id"]
            if actor_id not in world.actors:
                raise FeasibilityError("bound actor no longer exists")
            if actor_id in world.identity_bindings:
                raise FeasibilityError("actor identity already bound")
            if any((value["world_id"], value["entity_id"])
                   == (record["world_id"], record["entity_id"])
                   for value in world.identity_bindings.values()):
                raise FeasibilityError("ACE identity already assigned")
            if world.time_s != record["bound_at_s"]:
                raise FeasibilityError("binding grant is stale")
            world.identity_bindings[actor_id] = deepcopy(record)
            return {"actor_id": actor_id, "world_id": record["world_id"],
                    "entity_id": record["entity_id"],
                    "binding_sha256": record["binding_sha256"],
                    "scope": "synthetic_fixture_only",
                    "source_canon_promoted": False}

        return self._commit("fixture_identity_bound", record["actor_id"],
                            record["grant_ref"], change)

    def propose_relief(self, proposal: "ReliefProposal", *, cause: str) -> Receipt:
        """Commit a state-bound, synthetic noncombat policy proposal."""
        from .political_actions import commit_relief_proposal

        return commit_relief_proposal(self, proposal, cause=cause)

    def cast_relief_vote(self, motion_id: str, voter_id: str,
                         approve: bool, *, cause: str) -> Receipt:
        from .political_actions import cast_relief_vote

        return cast_relief_vote(self, motion_id, voter_id, approve, cause=cause)

    def ratify_relief(self, motion_id: str, officer_id: str, *,
                      cause: str) -> Receipt:
        from .political_actions import ratify_relief

        return ratify_relief(self, motion_id, officer_id, cause=cause)

    def dispatch_ratified_relief(self, motion_id: str,
                                 executor_id: str, *, cause: str) -> Receipt:
        from .political_actions import dispatch_ratified_relief

        return dispatch_ratified_relief(self, motion_id, executor_id, cause=cause)

    def send_policy_notice(self, motion_id: str, sender_id: str,
                           recipient_id: str, route_id: str, *,
                           cause: str) -> Receipt:
        """Send a typed proposal notice over a real outgoing information route."""
        from .distributed_actions import send_policy_notice

        return send_policy_notice(
            self, motion_id, sender_id, recipient_id, route_id, cause=cause)

    def submit_remote_ballot(self, motion_id: str, voter_id: str,
                             approve: bool, return_route_id: str, *,
                             cause: str) -> Receipt:
        """Transmit remote intent; it becomes a ballot only at arrival."""
        from .distributed_actions import submit_remote_ballot

        return submit_remote_ballot(
            self, motion_id, voter_id, approve, return_route_id, cause=cause)

    def offer_charter(self, founder_id: str, invitee_id: str, purpose: str,
                      outbound_route_id: str, *,
                      expires_s: int, cause: str) -> Receipt:
        from .federated_actions import offer_charter

        return offer_charter(self, founder_id, invitee_id, purpose,
                             outbound_route_id, expires_s=expires_s, cause=cause)

    def respond_charter(self, charter_id: str, invitee_id: str, accept: bool,
                        return_route_id: str, *, cause: str) -> Receipt:
        from .federated_actions import respond_charter

        return respond_charter(self, charter_id, invitee_id, accept,
                               return_route_id, cause=cause)

    def confirm_association(self, association_id: str, founder_id: str, *,
                            cause: str) -> Receipt:
        from .federated_actions import confirm_association

        return confirm_association(self, association_id, founder_id, cause=cause)

    def propose_mandate(self, association_id: str, proposer_id: str,
                        request: "MandateRequest", *, cause: str) -> Receipt:
        from .federated_actions import propose_mandate

        return propose_mandate(
            self, association_id, proposer_id, request, cause=cause)

    def respond_mandate(self, mandate_id: str, voter_id: str, approve: bool,
                        return_route_id: str, *, cause: str) -> Receipt:
        from .federated_actions import respond_mandate

        return respond_mandate(
            self, mandate_id, voter_id, approve, return_route_id, cause=cause)

    def execute_mandate(self, mandate_id: str, custodian_id: str, *,
                        cause: str) -> Receipt:
        from .federated_actions import execute_mandate

        return execute_mandate(self, mandate_id, custodian_id, cause=cause)

    @staticmethod
    def _id(world: Universe, prefix: str) -> str:
        world.next_serial += 1
        return f"{prefix}-{world.next_serial:08d}"

    @staticmethod
    def _route(world: Universe, route_id: str) -> Corridor:
        if route_id not in world.corridors:
            raise FeasibilityError("corridor not in the established field")
        route = world.corridors[route_id]
        if not route.enabled:
            raise FeasibilityError("corridor is inaccessible")
        return route

    @staticmethod
    def _require_fixture_cause(cause: str) -> None:
        if not cause.startswith("fixture:"):
            raise FeasibilityError("external field changes require fixture provenance")

    def disrupt_route(self, route_id: str, new_capacity: int, *, cause: str) -> Receipt:
        """Scripted physical disturbance of an open corridor's throughput.

        Capacity is the throughput of a corridor that exists, so it must stay
        a positive integer (the P0 invariant in ``Universe.validate``). A
        disruption to zero would be a second, partial encoding of closure:
        cargo blocked but signals still flowing. It is refused here, before
        any candidate state is built; use :meth:`close_route` instead.
        """
        if type(new_capacity) is not int or new_capacity < 1:
            raise FeasibilityError(
                "capacity must be a positive integer; use close_route for a full closure")
        self._require_fixture_cause(cause)

        def change(world: Universe) -> dict[str, Any]:
            if route_id not in world.corridors:
                raise FeasibilityError("unknown corridor")
            route = world.corridors[route_id]
            old = route.capacity_units_per_window
            route.capacity_units_per_window = new_capacity
            return {"route_id": route_id, "old_capacity": old,
                    "new_capacity": new_capacity}
        return self._commit("route_capacity_changed", None, cause, change)

    def close_route(self, route_id: str, *, cause: str) -> Receipt:
        """Scripted full corridor closure: no new cargo or signals may enter.

        Closure sets ``Corridor.enabled`` to False, so every access path that
        resolves the corridor through ``_route`` refuses it. Capacity is left
        untouched and applies again on reopening. Cargo and signals already
        in transit were committed before the closure and still arrive.
        """
        return self._set_route_enabled(route_id, False, "route_closed", cause)

    def reopen_route(self, route_id: str, *, cause: str) -> Receipt:
        """Scripted reversal of :meth:`close_route` with the prior capacity."""
        return self._set_route_enabled(route_id, True, "route_reopened", cause)

    def _set_route_enabled(self, route_id: str, enabled: bool, kind: str,
                           cause: str) -> Receipt:
        self._require_fixture_cause(cause)

        def change(world: Universe) -> dict[str, Any]:
            if route_id not in world.corridors:
                raise FeasibilityError("unknown corridor")
            route = world.corridors[route_id]
            if route.enabled is enabled:
                raise FeasibilityError(
                    "corridor is already " + ("open" if enabled else "closed"))
            route.enabled = enabled
            return {"route_id": route_id, "enabled": enabled,
                    "capacity_units_per_window": route.capacity_units_per_window}
        return self._commit(kind, None, cause, change)

    def dispatch(self, actor_id: str, route_id: str, commodity: str, amount: int,
                 *, cause: str) -> Receipt:
        if type(amount) is not int or amount <= 0:
            raise FeasibilityError("shipment must have a positive integer amount")
        if not commodity or commodity == "energy_j":
            raise FeasibilityError("unsupported commodity")

        def change(world: Universe) -> dict[str, Any]:
            if actor_id not in world.actors:
                raise FeasibilityError("unknown actor")
            actor = world.actors[actor_id]
            route = self._route(world, route_id)
            if actor.site_id != route.origin_id:
                raise FeasibilityError("actor lacks physical access to origin")
            site = world.sites[route.origin_id]
            window = world.time_s // route.window_seconds
            usage_key = f"{route.corridor_id}@{window}"
            used = world.capacity_used.get(usage_key, 0)
            if used + amount > route.capacity_units_per_window:
                raise FeasibilityError("corridor capacity exceeded")
            if site.inventory.get(commodity, 0) < amount:
                raise FeasibilityError("cargo unavailable")
            energy = route.distance_km * amount * route.shipment_energy_j_per_unit_km
            if site.inventory.get("energy_j", 0) < energy:
                raise FeasibilityError("insufficient transportation energy")
            site.inventory[commodity] -= amount
            site.inventory["energy_j"] -= energy
            world.heat_j += energy
            world.capacity_used[usage_key] = used + amount
            shipment_id = self._id(world, "shipment")
            due = world.time_s + _travel_seconds(route.distance_km,
                                                route.cargo_speed_km_s)
            world.in_transit[shipment_id] = Shipment(
                shipment_id, route_id, commodity, amount, actor_id,
                route.destination_id, world.time_s, due)
            scheduled_id = self._id(world, "scheduled")
            world.pending.append(ScheduledEvent(
                scheduled_id, due, world.next_serial, "cargo_arrival",
                {"shipment_id": shipment_id}))
            return {"shipment_id": shipment_id, "route_id": route_id,
                    "commodity": commodity, "amount": amount, "arrival_s": due,
                    "energy_to_heat_j": energy,
                    "institutionally_authorized":
                        site.site_id in actor.authorized_dispatch_sites}
        return self._commit("shipment_departed", actor_id, cause, change)

    def send_report(self, actor_id: str, recipient_id: str, route_id: str,
                    text: str, *, cause: str) -> Receipt:
        if not isinstance(text, str) or not 0 < len(text) <= 512:
            raise FeasibilityError("invalid report text")

        def change(world: Universe) -> dict[str, Any]:
            if actor_id not in world.actors or recipient_id not in world.actors:
                raise FeasibilityError("unknown sender or recipient")
            sender, recipient = world.actors[actor_id], world.actors[recipient_id]
            route = self._route(world, route_id)
            if sender.site_id != route.origin_id or recipient.site_id != route.destination_id:
                raise FeasibilityError("no established information path")
            energy = route.distance_km * route.signal_energy_j_per_km
            site = world.sites[sender.site_id]
            if site.inventory.get("energy_j", 0) < energy:
                raise FeasibilityError("insufficient signal energy")
            site.inventory["energy_j"] -= energy
            world.heat_j += energy
            due = world.time_s + _travel_seconds(route.distance_km,
                                                route.signal_speed_km_s)
            scheduled_id = self._id(world, "scheduled")
            world.pending.append(ScheduledEvent(scheduled_id, due,
                world.next_serial, "report_arrival",
                {"sender": actor_id, "recipient": recipient_id, "text": text,
                 "sent_s": world.time_s, "route_id": route_id}))
            return {"scheduled_id": scheduled_id, "recipient": recipient_id,
                    "arrival_s": due, "energy_to_heat_j": energy}
        return self._commit("report_sent", actor_id, cause, change)

    def advance_to(self, time_s: int) -> list[Receipt]:
        if type(time_s) is not int or time_s < self._state.time_s:
            raise FeasibilityError("simulation clock cannot run backward")
        committed: list[Receipt] = []
        while True:
            ready = sorted((e for e in self._state.pending if e.due_s <= time_s),
                           key=lambda e: (e.due_s, e.order))
            if not ready:
                break
            event = ready[0]

            def deliver(world: Universe) -> dict[str, Any]:
                matches = [e for e in world.pending if e.scheduled_id == event.scheduled_id]
                if len(matches) != 1:
                    raise AssertionError("scheduled event missing or duplicated")
                world.pending.remove(matches[0])
                world.time_s = event.due_s
                if event.kind == "cargo_arrival":
                    shipment = world.in_transit.pop(event.payload["shipment_id"])
                    dest = world.sites[shipment.destination_id]
                    dest.inventory[shipment.cargo_name] = (
                        dest.inventory.get(shipment.cargo_name, 0) + shipment.amount)
                    return {"shipment_id": shipment.shipment_id,
                            "destination": dest.site_id,
                            "delivered": shipment.amount,
                            "commodity": shipment.cargo_name}
                if event.kind == "report_arrival":
                    payload = dict(event.payload)
                    actor = world.actors[payload["recipient"]]
                    actor.received_reports.append({
                        "from": payload["sender"], "text": payload["text"],
                        "sent_s": payload["sent_s"], "received_s": world.time_s,
                        "route_id": payload["route_id"]})
                    return {"recipient": actor.actor_id, "from": payload["sender"],
                            "sent_s": payload["sent_s"]}
                if event.kind == "policy_notice_arrival":
                    from .distributed_actions import deliver_policy_notice

                    return deliver_policy_notice(world, event.payload)
                if event.kind == "policy_ballot_arrival":
                    from .distributed_actions import deliver_remote_ballot

                    return deliver_remote_ballot(world, event.payload["ballot_id"])
                if event.kind in {
                    "charter_offer_arrival", "charter_response_arrival",
                    "charter_expiry", "association_confirm_arrival",
                    "mandate_offer_arrival", "mandate_vote_arrival",
                    "mandate_expiry",
                }:
                    from .federated_actions import deliver_federated_event

                    return deliver_federated_event(world, event.kind, event.payload)
                if event.kind == "policy_expiry":
                    motion = world.relief_motions[event.payload["motion_id"]]
                    old_status = motion.status
                    returned = motion.escrow_amount
                    if returned:
                        institution = world.institutions[motion.institution_id]
                        site = world.sites[institution.seat_site_id]
                        site.inventory[motion.commodity] = (
                            site.inventory.get(motion.commodity, 0) + returned)
                        motion.escrow_amount = 0
                    if motion.status in ("proposed", "ratified"):
                        motion.status = "expired"
                        motion.approved_at_s = None
                    return {"motion_id": motion.motion_id,
                            "previous_status": old_status, "status": motion.status,
                            "resource_released": returned,
                            "commodity": motion.commodity,
                            "canonical_authority": False}
                raise AssertionError("unsupported scheduled event")

            committed.append(self._commit(event.kind, None,
                                          f"scheduled:{event.scheduled_id}", deliver))
        if self._state.time_s < time_s:
            def progress(world: Universe) -> dict[str, Any]:
                world.time_s = time_s
                return {"time_s": time_s}
            committed.append(self._commit("clock_advanced", None,
                                          "scheduler:advance", progress))
        return committed

    def site_view(self, site_id: str) -> dict[str, Any]:
        site = self._state.sites[site_id]
        result = {"site_id": site_id, "polity_id": site.polity_id,
                  "time_s": self._state.time_s, "inventory": dict(site.inventory)}
        reserved: dict[str, int] = {}
        for motion in self._state.relief_motions.values():
            if motion.escrow_amount and (
                self._state.institutions[motion.institution_id].seat_site_id == site_id
            ):
                reserved[motion.commodity] = (
                    reserved.get(motion.commodity, 0) + motion.escrow_amount)
        if reserved:
            result["reserved"] = reserved
        return result

    def polity_view(self, polity_id: str) -> dict[str, Any]:
        """Authoritative aggregate, not a claim of anyone's personal knowledge."""
        sites = sorted(s.site_id for s in self._state.sites.values()
                       if s.polity_id == polity_id)
        available: dict[str, int] = {}
        incoming: dict[str, int] = {}
        for site_id in sites:
            for commodity, amount in self._state.sites[site_id].inventory.items():
                available[commodity] = available.get(commodity, 0) + amount
        for shipment in self._state.in_transit.values():
            if shipment.destination_id in sites:
                incoming[shipment.cargo_name] = (
                    incoming.get(shipment.cargo_name, 0) + shipment.amount)
        result = {"polity_id": polity_id, "time_s": self._state.time_s,
                  "sites": sites, "available": available, "incoming": incoming}
        reserved: dict[str, int] = {}
        for site_id in sites:
            for commodity, amount in self.site_view(site_id).get("reserved", {}).items():
                reserved[commodity] = reserved.get(commodity, 0) + amount
        if reserved:
            result["reserved"] = reserved
        return result

    def actor_view(self, actor_id: str) -> dict[str, Any]:
        """Only local inventory and actually delivered reports are visible."""
        actor = self._state.actors[actor_id]
        return {"actor_id": actor_id, "time_s": self._state.time_s,
                "local": self.site_view(actor.site_id),
                "received_reports": deepcopy(actor.received_reports)}

    def evidence(self) -> dict[str, Any]:
        return {"run_id": self.run_id, "schema": "gumas.unified.p0.v1",
                "authority": "L2_synthetic_only", "initial_state": self.initial_hash,
                "final_state": self._state.digest(),
                "resource_totals": self._state.totals(),
                "ledger": [asdict(receipt) for receipt in self._ledger],
                "ledger_valid": verify_ledger(self._ledger, self.initial_hash,
                                              self._state.digest())}
