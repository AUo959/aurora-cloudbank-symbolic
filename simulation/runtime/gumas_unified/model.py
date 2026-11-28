"""Small, explicit, integer-unit L2 world model for GUMAS Unified P0.

All state is synthetic fixture state until an independently authorized source
adapter is connected. No CanonRec import, L1 handle, or external I/O occurs.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from typing import Any

from .federated_model import Association, Charter, Mandate, validate_federated_world


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
class Institution:
    """One synthetic local deliberative institution; never universal polity law."""
    institution_id: str
    seat_site_id: str
    members: tuple[str, ...]
    quorum: int
    approval_threshold: int
    polity_id: str


@dataclass(frozen=True)
class GovernanceProtocol:
    """A local decision rule, not a civilization or polity classification.

    Synthetic-only: P4 cannot import canonical authority or execute L1 work.
    """
    institution_id: str
    kind: str
    delegate_id: str | None = None
    veto_ids: tuple[str, ...] = ()


@dataclass
class ReliefMotion:
    """Proposed and voted resource allocation, not a rebellion probability."""
    motion_id: str
    institution_id: str
    proposer_id: str
    route_id: str
    commodity: str
    amount: int
    expires_s: int
    votes: dict[str, bool] = field(default_factory=dict)
    status: str = "proposed"
    escrow_amount: int = 0
    approved_at_s: int | None = None
    shipment_id: str | None = None


@dataclass
class RemoteBallot:
    """A sent but not necessarily counted synthetic remote political ballot."""
    ballot_id: str
    motion_id: str
    voter_id: str
    route_id: str
    approve: bool
    sent_s: int
    arrives_s: int
    notice_sha256: str
    status: str = "in_flight"


SCHEDULED_EVENT_KINDS = (
    "cargo_arrival", "report_arrival", "policy_expiry",
    "policy_notice_arrival", "policy_ballot_arrival",
    "charter_offer_arrival", "charter_response_arrival",
    "charter_expiry", "association_confirm_arrival",
    "mandate_offer_arrival", "mandate_vote_arrival",
    "mandate_expiry",
)


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
    if type(route.enabled) is not bool:
        raise ValueError("route enabled must be a boolean")
    _validate_corridor_speeds(route, profile)


def _validate_corridor_speeds(route: Any, profile: PhysicsProfile) -> None:
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


def _validate_pending_event(world: Any, event: Any) -> None:
    _natural(event.due_s, "pending due")
    _natural(event.order, "pending order")
    if event.due_s < world.time_s:
        raise ValueError("scheduled event in the past")
    if event.kind not in SCHEDULED_EVENT_KINDS:
        raise ValueError("unknown scheduled event")


_FIXTURE_BINDING_SCHEMA = "gumas.unified.fixture_identity_binding.p2"
_FIXTURE_BINDING_FALSE_FLAGS = (
    "grant_authenticated", "source_canon_promoted",
    "actor_permissions_changed", "agent_memory_injected",
)
_MOTION_STATUSES = ("proposed", "ratified", "dispatched", "rejected", "expired")
_HEX_DIGITS = "0123456789abcdef"


def _canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False, allow_nan=False).encode("utf-8")
    ).hexdigest()


def _signal_travel_s(route: Any) -> int:
    return (route.distance_km + route.signal_speed_km_s - 1) // route.signal_speed_km_s


def is_sha256_hex(value: Any) -> bool:
    """Lowercase 64-character hexadecimal string (shape only, not authenticity)."""
    return (isinstance(value, str) and len(value) == 64
            and all(c in _HEX_DIGITS for c in value))


# --- P2 fixture identity bindings ------------------------------------------

def _binding_authorized(world: Any, actor_id: str, record: dict[str, Any]) -> bool:
    if actor_id not in world.actors or record.get("actor_id") != actor_id:
        return False
    if record.get("schema") != _FIXTURE_BINDING_SCHEMA:
        return False
    if record.get("scope") != "synthetic_fixture_only":
        return False
    return all(record.get(flag) is False for flag in _FIXTURE_BINDING_FALSE_FLAGS)


def _claim_binding_reference(record: dict[str, Any], bound: set[tuple[str, str]]) -> None:
    key = (record.get("world_id"), record.get("entity_id"))
    if not all(isinstance(value, str) and value for value in key):
        raise ValueError("invalid identity reference")
    if key in bound:
        raise ValueError("duplicate ACE identity binding")
    bound.add(key)


def _validate_binding_interval(world: Any, record: dict[str, Any]) -> None:
    _natural(record.get("bound_at_s"), "identity bound_at_s")
    _natural(record.get("valid_until_s"), "identity valid_until_s")
    if (record["bound_at_s"] > world.time_s
            or record["valid_until_s"] <= record["bound_at_s"]):
        raise ValueError("identity binding has invalid validity interval")


def _validate_identity_binding(world: Any, actor_id: str, record: Any,
                               bound: set[tuple[str, str]]) -> None:
    if not isinstance(record, dict):
        raise ValueError("identity binding must be an object")
    if not _binding_authorized(world, actor_id, record):
        raise ValueError("unauthorized or inconsistent L2 fixture identity binding")
    _claim_binding_reference(record, bound)
    _validate_binding_interval(world, record)
    payload = {k: v for k, v in record.items() if k != "binding_sha256"}
    if record.get("binding_sha256") != _canonical_sha256(payload):
        raise ValueError("identity binding fingerprint does not match record")


def _validate_identity_bindings(world: Any) -> None:
    bound: set[tuple[str, str]] = set()
    for actor_id, record in world.identity_bindings.items():
        _validate_identity_binding(world, actor_id, record, bound)


# --- P3 institutions and P4 governance protocols ----------------------------

def _institution_members_valid(world: Any, institution: Any) -> bool:
    members = institution.members
    return (bool(members) and len(set(members)) == len(members)
            and all(m in world.actors for m in members))


def _validate_institution(world: Any, key: str, institution: Any) -> None:
    if key != institution.institution_id or institution.seat_site_id not in world.sites:
        raise ValueError("invalid institution identity or seat")
    if world.sites[institution.seat_site_id].polity_id != institution.polity_id:
        raise ValueError("institution polity does not match its local seat")
    if not _institution_members_valid(world, institution):
        raise ValueError("institution must have distinct, existing members")
    _natural(institution.quorum, "institution quorum", positive=True)
    _natural(institution.approval_threshold, "approval threshold", positive=True)
    if (institution.quorum > len(institution.members)
            or institution.approval_threshold > institution.quorum):
        raise ValueError("impossible institution quorum or approval threshold")


def _validate_institutions(world: Any) -> None:
    for key, institution in world.institutions.items():
        _validate_institution(world, key, institution)


def _validate_governance_rules(world: Any) -> None:
    from .governance_rules import validate_protocol

    for key, rule in world.governance_rules.items():
        if key not in world.institutions or not isinstance(rule, GovernanceProtocol):
            raise ValueError("governance protocol refers to an absent institution")
        validate_protocol(world.institutions[key], rule)


# --- P3 relief motions ------------------------------------------------------

def _validate_motion_identity(world: Any, key: str, motion: Any) -> None:
    if key != motion.motion_id or motion.institution_id not in world.institutions:
        raise ValueError("invalid relief motion identity or institution")
    institution = world.institutions[motion.institution_id]
    if motion.proposer_id not in institution.members:
        raise ValueError("motion proposer not a member")
    if motion.route_id not in world.corridors:
        raise ValueError("motion references nonexistent corridor")
    if world.corridors[motion.route_id].origin_id != institution.seat_site_id:
        raise ValueError("motion route not connected to institution seat")


def _validate_motion_terms(motion: Any) -> None:
    if not motion.commodity or motion.commodity == "energy_j":
        raise ValueError("invalid motion commodity")
    _natural(motion.amount, "motion amount", positive=True)
    _natural(motion.expires_s, "motion expiry", positive=True)
    _natural(motion.escrow_amount, "motion escrow")
    if (motion.status not in _MOTION_STATUSES
            or motion.escrow_amount not in (0, motion.amount)
            or (motion.status == "ratified") != (motion.escrow_amount == motion.amount)):
        raise ValueError("inconsistent motion status or escrow")


def _validate_motion_shipment_ref(motion: Any) -> None:
    if motion.status == "dispatched" and not motion.shipment_id:
        raise ValueError("dispatched motion missing shipment reference")
    if motion.status != "dispatched" and motion.shipment_id is not None:
        raise ValueError("motion shipment reference without dispatch")


def _motion_approval_recorded(world: Any, motion: Any) -> bool:
    from .governance_rules import approval_ready

    approved = motion.approved_at_s
    return (approved is not None and type(approved) is int
            and 0 <= approved < motion.expires_s
            and approval_ready(world, motion))


def _validate_motion_votes(world: Any, motion: Any) -> None:
    from .governance_rules import ballot_eligible

    if any(type(vote) is not bool or not ballot_eligible(world, motion, voter)
           for voter, vote in motion.votes.items()):
        raise ValueError("unauthorized or invalid policy ballot")
    if motion.status in ("ratified", "dispatched") and not _motion_approval_recorded(world, motion):
        raise ValueError("motion lacks sufficient recorded approval")
    if motion.status in ("proposed", "rejected", "expired") and motion.approved_at_s is not None:
        raise ValueError("unapproved motion has approval timestamp")


def _validate_relief_motions(world: Any) -> None:
    for key, motion in world.relief_motions.items():
        _validate_motion_identity(world, key, motion)
        _validate_motion_terms(motion)
        _validate_motion_shipment_ref(motion)
        _validate_motion_votes(world, motion)


# --- P5 remote ballots --------------------------------------------------------

def _remote_ballot_motion(world: Any, key: str, ballot: Any) -> Any:
    if not isinstance(ballot, RemoteBallot) or key != ballot.ballot_id:
        raise ValueError("invalid remote ballot record")
    if ballot.motion_id not in world.relief_motions:
        raise ValueError("remote ballot refers to missing motion")
    return world.relief_motions[ballot.motion_id]


def _validate_ballot_voter(world: Any, motion: Any, ballot: Any) -> None:
    from .governance_rules import ballot_eligible

    if (ballot.voter_id not in world.actors
            or not ballot_eligible(world, motion, ballot.voter_id)
            or ballot.route_id not in world.corridors
            or type(ballot.approve) is not bool):
        raise ValueError("remote ballot has invalid voter, rule or route")


def _validate_ballot_direction(world: Any, institution: Any, ballot: Any) -> None:
    actor = world.actors[ballot.voter_id]
    corridor = world.corridors[ballot.route_id]
    if (actor.site_id == institution.seat_site_id
            or corridor.origin_id != actor.site_id
            or corridor.destination_id != institution.seat_site_id):
        raise ValueError("remote ballot lacks directed information path")


def _validate_ballot_timing(world: Any, ballot: Any) -> None:
    _natural(ballot.sent_s, "remote ballot sent_s")
    _natural(ballot.arrives_s, "remote ballot arrives_s")
    travel = _signal_travel_s(world.corridors[ballot.route_id])
    if (ballot.sent_s > world.time_s
            or ballot.arrives_s != ballot.sent_s + travel
            or not is_sha256_hex(ballot.notice_sha256)):
        raise ValueError("remote ballot has invalid timing or notice fingerprint")


def _ballot_notice_delivered(world: Any, motion: Any, ballot: Any) -> bool:
    from .distributed_actions import public_motion_terms

    actor = world.actors[ballot.voter_id]
    matching_notice = [
        report for report in actor.received_reports
        if (report.get("kind") == "policy_motion_notice"
            and report.get("motion_id") == ballot.motion_id
            and report.get("motion_sha256") == ballot.notice_sha256
            and report.get("proposal") == public_motion_terms(motion)
            and report.get("received_s", world.time_s + 1) <= ballot.sent_s)
    ]
    return bool(matching_notice)


def _ballot_receipt_scheduled(world: Any, motion: Any, ballot: Any) -> bool:
    return ballot.voter_id not in motion.votes and any(
        e.kind == "policy_ballot_arrival"
        and e.payload.get("ballot_id") == ballot.ballot_id
        and e.due_s == ballot.arrives_s for e in world.pending
    )


def _validate_ballot_status(world: Any, motion: Any, ballot: Any) -> None:
    if ballot.status == "in_flight":
        if not _ballot_receipt_scheduled(world, motion, ballot):
            raise ValueError("remote ballot in flight missing scheduled receipt")
    elif ballot.status == "counted":
        if (ballot.arrives_s > world.time_s
                or motion.votes.get(ballot.voter_id) is not ballot.approve):
            raise ValueError("remote counted ballot not present in institution")
    elif ballot.status == "arrived_unusable":
        if ballot.arrives_s > world.time_s:
            raise ValueError("unusable remote ballot has not arrived")
    else:
        raise ValueError("unknown remote ballot status")


def _validate_remote_ballot(world: Any, key: str, ballot: Any,
                            seen: set[tuple[str, str]]) -> None:
    motion = _remote_ballot_motion(world, key, ballot)
    institution = world.institutions[motion.institution_id]
    _validate_ballot_voter(world, motion, ballot)
    _validate_ballot_direction(world, institution, ballot)
    _validate_ballot_timing(world, ballot)
    pair = (ballot.motion_id, ballot.voter_id)
    if pair in seen:
        raise ValueError("duplicate remote voter intent")
    seen.add(pair)
    if not _ballot_notice_delivered(world, motion, ballot):
        raise ValueError("remote ballot lacks prior delivered motion notice")
    _validate_ballot_status(world, motion, ballot)


def _validate_remote_ballots(world: Any) -> None:
    seen: set[tuple[str, str]] = set()
    for key, ballot in world.remote_ballots.items():
        _validate_remote_ballot(world, key, ballot, seen)


# --- P3/P5 scheduled political events ---------------------------------------

def _validate_policy_expiry_event(world: Any, event: Any) -> None:
    motion = world.relief_motions.get(event.payload.get("motion_id"))
    if motion is None or motion.expires_s != event.due_s:
        raise ValueError("policy expiry event lacks matching motion")


def _notice_route_matches(institution: Any, sender: Any, recipient: Any, route: Any) -> bool:
    return (sender.actor_id in institution.members
            and recipient.actor_id in institution.members
            and sender.site_id == route.origin_id
            and recipient.site_id == route.destination_id
            and route.origin_id == institution.seat_site_id
            and route.destination_id != route.origin_id)


def _notice_terms_match(world: Any, event: Any, motion: Any, route: Any) -> bool:
    from .distributed_actions import motion_fingerprint, public_motion_terms

    payload = event.payload
    return (payload.get("motion_sha256") == motion_fingerprint(motion)
            and payload.get("proposal") == public_motion_terms(motion)
            and type(payload.get("sent_s")) is int
            and payload["sent_s"] <= world.time_s
            and event.due_s == payload["sent_s"] + _signal_travel_s(route))


def _policy_notice_supported(world: Any, event: Any) -> bool:
    payload = event.payload
    motion = world.relief_motions.get(payload.get("motion_id"))
    recipient = world.actors.get(payload.get("recipient"))
    sender = world.actors.get(payload.get("sender"))
    route = world.corridors.get(payload.get("route_id"))
    if motion is None or recipient is None or sender is None or route is None:
        return False
    institution = world.institutions[motion.institution_id]
    return (_notice_route_matches(institution, sender, recipient, route)
            and _notice_terms_match(world, event, motion, route))


def _validate_policy_notice_event(world: Any, event: Any) -> None:
    if not _policy_notice_supported(world, event):
        raise ValueError("policy notice lacks physically supported provenance")


def _validate_policy_ballot_event(world: Any, event: Any) -> None:
    ballot = world.remote_ballots.get(event.payload.get("ballot_id"))
    if ballot is None or ballot.status != "in_flight" or event.due_s != ballot.arrives_s:
        raise ValueError("policy ballot event lacks in-flight ballot")


_POLITICAL_EVENT_CHECKS = {
    "policy_expiry": _validate_policy_expiry_event,
    "policy_notice_arrival": _validate_policy_notice_event,
    "policy_ballot_arrival": _validate_policy_ballot_event,
}


def _validate_pending_events(world: Any) -> None:
    for event in world.pending:
        _validate_pending_event(world, event)
        check = _POLITICAL_EVENT_CHECKS.get(event.kind)
        if check is not None:
            check(world, event)


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
    institutions: dict[str, Institution] = field(default_factory=dict)
    relief_motions: dict[str, ReliefMotion] = field(default_factory=dict)
    governance_rules: dict[str, GovernanceProtocol] = field(default_factory=dict)
    remote_ballots: dict[str, RemoteBallot] = field(default_factory=dict)
    charters: dict[str, Charter] = field(default_factory=dict)
    associations: dict[str, Association] = field(default_factory=dict)
    mandates: dict[str, Mandate] = field(default_factory=dict)

    def validate(self, profile: PhysicsProfile) -> None:
        # Order is part of the contract: the first failing section's error is
        # the transaction's rejection reason. Each layer's section is a helper.
        _validate_scalars(self)
        _validate_profile(profile)
        _validate_sites(self)
        _validate_actors(self)
        _validate_identity_bindings(self)
        _validate_institutions(self)
        _validate_governance_rules(self)
        _validate_relief_motions(self)
        _validate_corridors(self, profile)
        _validate_in_transit(self)
        _validate_remote_ballots(self)
        _validate_capacity(self)
        _validate_pending_events(self)
        validate_federated_world(self)

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
        for motion in self.relief_motions.values():
            if motion.escrow_amount:
                key = motion.commodity
                totals[key] = totals.get(key, 0) + motion.escrow_amount
        totals["energy_j"] = totals.get("energy_j", 0) + self.heat_j
        return {k: v for k, v in totals.items() if v != 0}

    def digest(self) -> str:
        payload = asdict(self)
        # Empty P2 identity storage is not a new fact: preserve exact P0/P1
        # state hashes and existing historical replay receipts.
        if not payload["identity_bindings"]:
            payload.pop("identity_bindings")
        if not payload["institutions"]:
            payload.pop("institutions")
        if not payload["relief_motions"]:
            payload.pop("relief_motions")
        if not payload["governance_rules"]:
            payload.pop("governance_rules")
        if not payload["remote_ballots"]:
            payload.pop("remote_ballots")
        for field_name in ("charters", "associations", "mandates"):
            if not payload[field_name]:
                payload.pop(field_name)
        data = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
        return hashlib.sha256(data).hexdigest()
