"""P3: one explicitly synthetic, noncombat institution-to-physics action path.

A relief motion requires a local proposer, independently recorded ballots,
a quorum/threshold, stock reservation, and a separately feasible shipment.
No civilization-name multipliers, political hazard draws, unseen votes, or
external source authority. All commits go through the P0 causal kernel.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .external_evidence import canonical_sha256
from .kernel import CausalEngine, FeasibilityError, Receipt, _travel_seconds
from .model import ReliefMotion, ScheduledEvent, Shipment, Universe

SCHEMA = "gumas.unified.relief_proposal.p3"


@dataclass(frozen=True)
class ReliefProposal:
    schema: str
    run_id: str
    state_sha256: str
    institution_id: str
    proposer_id: str
    route_id: str
    commodity: str
    amount: int
    expires_s: int
    digest: str


def _proposal_digest(proposal: ReliefProposal) -> str:
    return canonical_sha256({
        k: v for k, v in asdict(proposal).items() if k != "digest"
    })


def _bounded(value: str, name: str) -> str:
    if not isinstance(value, str) or not 0 < len(value) <= 128 or not value.strip():
        raise FeasibilityError(f"{name} must be a bounded nonempty identifier")
    return value


def _positive(value: int, name: str) -> int:
    if type(value) is not int or not 0 < value <= 10**12:
        raise FeasibilityError(f"{name} must be a bounded positive integer")
    return value


def _institution_at_seat(world: Universe, institution_id: str,
                         actor_id: str, *, requires_membership: bool = True):
    institution = world.institutions.get(institution_id)
    actor = world.actors.get(actor_id)
    if institution is None or actor is None:
        raise FeasibilityError("institution or acting agent does not exist")
    if actor.site_id != institution.seat_site_id:
        raise FeasibilityError("agent lacks local presence at institution seat")
    if requires_membership and actor_id not in institution.members:
        raise FeasibilityError("agent has no recorded institutional membership")
    return institution


def _actor_binding(world: Universe, actor_id: str) -> str | None:
    record = world.identity_bindings.get(actor_id)
    if record and record["bound_at_s"] <= world.time_s < record["valid_until_s"]:
        return record["binding_sha256"]
    return None


def _motion(world: Universe, motion_id: str, status: str = "proposed") -> ReliefMotion:
    motion = world.relief_motions.get(motion_id)
    if motion is None:
        raise FeasibilityError("relief motion is not part of this simulated history")
    if motion.status != status:
        raise FeasibilityError(f"relief motion is {motion.status}, not {status}")
    if world.time_s >= motion.expires_s:
        raise FeasibilityError("relief motion has expired")
    return motion


def prepare_relief_proposal(engine: CausalEngine, *, institution_id: str,
                            proposer_id: str, route_id: str, commodity: str,
                            amount: int, expires_s: int) -> ReliefProposal:
    """Read-only, state-bound and deterministic policy proposal preparation."""
    if not isinstance(engine, CausalEngine) or not engine.run_id.startswith("synthetic-"):
        raise FeasibilityError("only synthetic L2 proposals are supported")
    world = engine.state
    _bounded(institution_id, "institution_id")
    _bounded(proposer_id, "proposer_id")
    _bounded(route_id, "route_id")
    _bounded(commodity, "commodity")
    _positive(amount, "amount")
    _positive(expires_s, "expires_s")
    if expires_s <= world.time_s or commodity == "energy_j":
        raise FeasibilityError("invalid motion expiry or reserved commodity")
    institution = _institution_at_seat(world, institution_id, proposer_id)
    route = engine._route(world, route_id)
    if route.origin_id != institution.seat_site_id:
        raise FeasibilityError("institution cannot allocate through a remote site")
    proposal = ReliefProposal(
        SCHEMA, engine.run_id, world.digest(), institution_id,
        proposer_id, route_id, commodity, amount, expires_s, "")
    return ReliefProposal(**{
        **asdict(proposal), "digest": _proposal_digest(proposal)
    })


def commit_relief_proposal(engine: CausalEngine, proposal: ReliefProposal,
                           *, cause: str) -> Receipt:
    if not isinstance(engine, CausalEngine) or not isinstance(proposal, ReliefProposal):
        raise FeasibilityError("invalid synthetic policy proposal")
    if (proposal.schema != SCHEMA or proposal.run_id != engine.run_id
            or proposal.digest != _proposal_digest(proposal)
            or proposal.state_sha256 != engine.state.digest()):
        raise FeasibilityError("policy proposal is stale, modified or for another run")
    _bounded(cause, "cause")

    def change(world: Universe) -> dict[str, Any]:
        institution = _institution_at_seat(
            world, proposal.institution_id, proposal.proposer_id)
        route = engine._route(world, proposal.route_id)
        if route.origin_id != institution.seat_site_id:
            raise FeasibilityError("relief source is outside the institution seat")
        if proposal.expires_s <= world.time_s:
            raise FeasibilityError("proposal already expired")
        motion_id = engine._id(world, "motion")
        world.relief_motions[motion_id] = ReliefMotion(
            motion_id, institution.institution_id, proposal.proposer_id,
            proposal.route_id, proposal.commodity, proposal.amount,
            proposal.expires_s)
        event_id = engine._id(world, "scheduled")
        world.pending.append(ScheduledEvent(
            event_id, proposal.expires_s, world.next_serial,
            "policy_expiry", {"motion_id": motion_id}))
        return {
            "motion_id": motion_id,
            "institution_id": institution.institution_id,
            "proposal_sha256": proposal.digest,
            "proposer_id": proposal.proposer_id,
            "proposer_binding_sha256": _actor_binding(world, proposal.proposer_id),
            "route_id": proposal.route_id,
            "commodity": proposal.commodity, "amount": proposal.amount,
            "expires_s": proposal.expires_s,
            "status": "proposed", "canonical_authority": False,
        }
    return engine._commit("relief_proposed", proposal.proposer_id, cause, change)


def cast_relief_vote(engine: CausalEngine, motion_id: str, voter_id: str,
                     approve: bool, *, cause: str) -> Receipt:
    if type(approve) is not bool:
        raise FeasibilityError("a ballot must be explicitly yes or no")
    _bounded(cause, "cause")

    def change(world: Universe) -> dict[str, Any]:
        motion = _motion(world, motion_id)
        institution = _institution_at_seat(
            world, motion.institution_id, voter_id)
        if voter_id in motion.votes:
            raise FeasibilityError("actor has already voted on this motion")
        motion.votes[voter_id] = approve
        yes_count = sum(motion.votes.values())
        no_count = len(motion.votes) - yes_count
        if len(institution.members) - no_count < institution.approval_threshold:
            motion.status = "rejected"
        return {"motion_id": motion_id, "voter_id": voter_id,
                "voter_binding_sha256": _actor_binding(world, voter_id),
                "approve": approve, "yes_votes": yes_count,
                "no_votes": no_count, "status": motion.status}
    return engine._commit("relief_vote_recorded", voter_id, cause, change)


def ratify_relief(engine: CausalEngine, motion_id: str,
                  officer_id: str, *, cause: str) -> Receipt:
    _bounded(cause, "cause")

    def change(world: Universe) -> dict[str, Any]:
        motion = _motion(world, motion_id)
        institution = _institution_at_seat(world, motion.institution_id, officer_id)
        if (len(motion.votes) < institution.quorum
                or sum(motion.votes.values()) < institution.approval_threshold):
            raise FeasibilityError("quorum or approval threshold not satisfied")
        route = engine._route(world, motion.route_id)
        site = world.sites[route.origin_id]
        if site.inventory.get(motion.commodity, 0) < motion.amount:
            raise FeasibilityError("institution lacks available resources to reserve")
        site.inventory[motion.commodity] -= motion.amount
        motion.escrow_amount = motion.amount
        motion.status = "ratified"
        motion.approved_at_s = world.time_s
        return {"motion_id": motion_id, "institution_id": institution.institution_id,
                "yes_votes": sum(motion.votes.values()),
                "ballots_cast": len(motion.votes),
                "reserved_at_site": site.site_id,
                "commodity": motion.commodity, "reserved_amount": motion.amount,
                "available_after_reservation": site.inventory[motion.commodity],
                "status": "ratified", "canonical_authority": False}
    return engine._commit("relief_ratified_and_reserved", officer_id, cause, change)


def dispatch_ratified_relief(engine: CausalEngine, motion_id: str,
                             executor_id: str, *, cause: str) -> Receipt:
    _bounded(cause, "cause")

    def change(world: Universe) -> dict[str, Any]:
        motion = _motion(world, motion_id, status="ratified")
        institution = _institution_at_seat(
            world, motion.institution_id, executor_id, requires_membership=False)
        route = engine._route(world, motion.route_id)
        if (route.origin_id != institution.seat_site_id
                or motion.escrow_amount != motion.amount):
            raise FeasibilityError("physical escrow or source is not available")
        window = world.time_s // route.window_seconds
        usage_key = f"{route.corridor_id}@{window}"
        used = world.capacity_used.get(usage_key, 0)
        if used + motion.amount > route.capacity_units_per_window:
            raise FeasibilityError("cargo exceeds available corridor capacity")
        site = world.sites[route.origin_id]
        energy = (route.distance_km * motion.amount
                  * route.shipment_energy_j_per_unit_km)
        if site.inventory.get("energy_j", 0) < energy:
            raise FeasibilityError("insufficient transport energy")
        site.inventory["energy_j"] -= energy
        world.heat_j += energy
        world.capacity_used[usage_key] = used + motion.amount
        shipment_id = engine._id(world, "shipment")
        due = world.time_s + _travel_seconds(route.distance_km, route.cargo_speed_km_s)
        world.in_transit[shipment_id] = Shipment(
            shipment_id, motion.route_id, motion.commodity, motion.amount,
            executor_id, route.destination_id, world.time_s, due)
        event_id = engine._id(world, "scheduled")
        world.pending.append(ScheduledEvent(
            event_id, due, world.next_serial, "cargo_arrival",
            {"shipment_id": shipment_id}))
        motion.escrow_amount = 0
        motion.status = "dispatched"
        motion.shipment_id = shipment_id
        return {"motion_id": motion_id, "shipment_id": shipment_id,
                "executor_id": executor_id,
                "executor_binding_sha256": _actor_binding(world, executor_id),
                "institutionally_authorized": executor_id in institution.members,
                "commodity": motion.commodity, "amount": motion.amount,
                "arrival_s": due, "energy_to_heat_j": energy,
                "status": "dispatched"}
    return engine._commit("relief_shipment_departed", executor_id, cause, change)


def institution_view(engine: CausalEngine, institution_id: str) -> dict[str, Any]:
    """An operator-only organizational projection of the committed state.

    This is not remote character knowledge or an assumption that all members
    share ballots instantaneously. P3 voters must be physically at the seat.
    """
    world = engine.state
    institution = world.institutions.get(institution_id)
    if institution is None:
        raise FeasibilityError("unknown institution")
    motions = {}
    for motion_id, motion in sorted(world.relief_motions.items()):
        if motion.institution_id == institution_id:
            motions[motion_id] = {
                "status": motion.status,
                "yes_votes": sum(motion.votes.values()),
                "no_votes": len(motion.votes) - sum(motion.votes.values()),
                "reserved": motion.escrow_amount,
                "commodity": motion.commodity,
                "amount": motion.amount,
                "shipment_id": motion.shipment_id,
                "expires_s": motion.expires_s,
            }
    return {"schema": "gumas.unified.institution_view.p3",
            "authority": "synthetic_operator_only",
            "institution_id": institution_id,
            "polity_id": institution.polity_id,
            "seat_site_id": institution.seat_site_id,
            "time_s": world.time_s,
            "membership_count": len(institution.members),
            "quorum": institution.quorum,
            "approval_threshold": institution.approval_threshold,
            "motions": motions}
