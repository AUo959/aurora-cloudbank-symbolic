"""P5 distributed political participation, constrained by P0 signal physics.

A remote actor must first receive a specific motion notice via a real directed
corridor. Their individually chosen ballot then travels back as a second
signal. Until it arrives, the institution has no ballot to count. Everything
is synthetic L2, with no networking, autonomous source authority or canon.
"""
from __future__ import annotations

from typing import Any

from .external_evidence import canonical_sha256
from .governance_rules import ballot_eligible, protocol_label, unreachable_approval
from .kernel import CausalEngine, FeasibilityError, Receipt, _travel_seconds
from .model import ReliefMotion, RemoteBallot, ScheduledEvent, Universe
from .political_actions import _actor_binding


def public_motion_terms(motion: ReliefMotion) -> dict[str, Any]:
    """Public, immutable proposal terms explicitly included in each notice."""
    return {
        "motion_id": motion.motion_id,
        "institution_id": motion.institution_id,
        "proposer_id": motion.proposer_id,
        "route_id": motion.route_id,
        "commodity": motion.commodity,
        "amount": motion.amount,
        "expires_s": motion.expires_s,
    }


def motion_fingerprint(motion: ReliefMotion) -> str:
    """Stable policy terms: no mutable ballots, outcomes or observation fields."""
    return canonical_sha256(public_motion_terms(motion))


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not 0 < len(value) <= 128 or not value.strip():
        raise FeasibilityError(f"{label} must be a bounded identifier")
    return value


def _active_motion(world: Universe, motion_id: str) -> ReliefMotion:
    motion = world.relief_motions.get(motion_id)
    if motion is None or motion.status != "proposed" or world.time_s >= motion.expires_s:
        raise FeasibilityError("motion is not open for participation")
    return motion


def _send_signal_energy(world: Universe, route) -> int:
    """Deduct P0 communication energy, retain it as heat, never invent resources."""
    energy = route.distance_km * route.signal_energy_j_per_km
    source = world.sites[route.origin_id]
    if source.inventory.get("energy_j", 0) < energy:
        raise FeasibilityError("insufficient source energy for political signal")
    source.inventory["energy_j"] -= energy
    world.heat_j += energy
    return energy


def _notice_endpoints(engine: CausalEngine, world: Universe, institution,
                      sender_id: str, recipient_id: str, route_id: str):
    """Return (recipient, route) for a directed seat-to-remote member notice."""
    if sender_id not in institution.members or recipient_id not in institution.members:
        raise FeasibilityError("policy notice participants must be known members")
    sender = world.actors[sender_id]
    recipient = world.actors[recipient_id]
    route = engine._route(world, route_id)
    if (sender.site_id != institution.seat_site_id
            or route.origin_id != sender.site_id
            or route.destination_id != recipient.site_id
            or recipient.site_id == institution.seat_site_id):
        raise FeasibilityError("policy notice needs a directed, remote information path")
    return recipient, route


def _notice_in_flight(world: Universe, motion_id: str, recipient_id: str) -> bool:
    return any(
        e.kind == "policy_notice_arrival"
        and e.payload.get("motion_id") == motion_id
        and e.payload.get("recipient") == recipient_id
        for e in world.pending
    )


def _notice_received(recipient, motion_id: str, digest: str) -> bool:
    return any(
        r.get("kind") == "policy_motion_notice"
        and r.get("motion_id") == motion_id
        and r.get("motion_sha256") == digest
        for r in recipient.received_reports
    )


def _schedule_signal(engine: CausalEngine, world: Universe, route, kind: str,
                     payload: dict[str, Any]) -> tuple[str, int]:
    """Queue a signal arrival at the corridor's light delay; return (event id, due)."""
    due = world.time_s + _travel_seconds(route.distance_km, route.signal_speed_km_s)
    scheduled_id = engine._id(world, "scheduled")
    world.pending.append(ScheduledEvent(scheduled_id, due, world.next_serial, kind, payload))
    return scheduled_id, due


def send_policy_notice(engine: CausalEngine, motion_id: str, sender_id: str,
                       recipient_id: str, route_id: str, *, cause: str) -> Receipt:
    """Send proposal knowledge outward. No remote decision without delivery."""
    for value, label in (
        (motion_id, "motion_id"), (sender_id, "sender_id"),
        (recipient_id, "recipient_id"), (route_id, "route_id"),
        (cause, "cause"),
    ):
        _identifier(value, label)

    def change(world: Universe) -> dict[str, Any]:
        motion = _active_motion(world, motion_id)
        institution = world.institutions[motion.institution_id]
        recipient, route = _notice_endpoints(
            engine, world, institution, sender_id, recipient_id, route_id)
        digest = motion_fingerprint(motion)
        if (_notice_in_flight(world, motion_id, recipient_id)
                or _notice_received(recipient, motion_id, digest)):
            raise FeasibilityError("this remote participant already has a motion notice")
        energy = _send_signal_energy(world, route)
        scheduled_id, due = _schedule_signal(engine, world, route, "policy_notice_arrival", {
            "motion_id": motion_id, "motion_sha256": digest,
            "proposal": public_motion_terms(motion),
            "sender": sender_id, "recipient": recipient_id,
            "route_id": route_id, "sent_s": world.time_s,
        })
        return {
            "motion_id": motion_id, "recipient_id": recipient_id,
            "motion_sha256": digest,
            "scheduled_id": scheduled_id, "arrival_s": due,
            "energy_to_heat_j": energy,
            "recipient_has_notice": False,
            "sender_binding_sha256": _actor_binding(world, sender_id),
            "scope": "synthetic_L2_only",
        }

    return engine._commit("policy_notice_sent", sender_id, cause, change)


def deliver_policy_notice(world: Universe, payload: dict[str, Any]) -> dict[str, Any]:
    """Called solely by the P0 scheduler after the delay is satisfied."""
    recipient_id = payload["recipient"]
    actor = world.actors[recipient_id]
    motion = world.relief_motions[payload["motion_id"]]
    digest = motion_fingerprint(motion)
    if (digest != payload["motion_sha256"]
            or payload.get("proposal") != public_motion_terms(motion)):
        raise FeasibilityError("scheduled policy notice content fingerprint drift")
    actor.received_reports.append({
        "kind": "policy_motion_notice",
        "motion_id": motion.motion_id,
        "institution_id": motion.institution_id,
        "motion_sha256": digest,
        "proposal": dict(payload["proposal"]),
        "from": payload["sender"],
        "route_id": payload["route_id"],
        "sent_s": payload["sent_s"],
        "received_s": world.time_s,
    })
    return {
        "motion_id": motion.motion_id, "recipient_id": recipient_id,
        "motion_sha256": digest, "sent_s": payload["sent_s"],
        "received_s": world.time_s, "scope": "synthetic_L2_only",
    }


def _remote_voter(world: Universe, motion_id: str, motion: ReliefMotion, institution,
                  voter_id: str):
    """Return the eligible, remote, not-yet-voted actor for this motion."""
    if not ballot_eligible(world, motion, voter_id):
        raise FeasibilityError("remote actor has no recorded voting authority")
    actor = world.actors[voter_id]
    if actor.site_id == institution.seat_site_id:
        raise FeasibilityError("seat-local voters use P3 direct ballots")
    if voter_id in motion.votes or any(
        b.motion_id == motion_id and b.voter_id == voter_id
        for b in world.remote_ballots.values()
    ):
        raise FeasibilityError("duplicate remote ballot attempt")
    return actor


def _notice_matches(world: Universe, notice: dict[str, Any], motion_id: str,
                    motion: ReliefMotion, digest: str) -> bool:
    return (notice.get("kind") == "policy_motion_notice"
            and notice.get("motion_id") == motion_id
            and notice.get("institution_id") == motion.institution_id
            and notice.get("motion_sha256") == digest
            and notice.get("proposal") == public_motion_terms(motion)
            and type(notice.get("received_s")) is int
            and notice["received_s"] <= world.time_s)


def _return_route(engine: CausalEngine, world: Universe, actor, institution, route_id: str):
    route = engine._route(world, route_id)
    if (route.origin_id != actor.site_id
            or route.destination_id != institution.seat_site_id):
        raise FeasibilityError("no directed return signal to institution")
    return route


def submit_remote_ballot(engine: CausalEngine, motion_id: str, voter_id: str,
                         approve: bool, return_route_id: str, *,
                         cause: str) -> Receipt:
    """An informed member's remote decision becomes an in-flight signal.

    The authorization rule is checked at send and receive; the ballot never
    counts until its directed signal reaches the institution seat.
    """
    if type(approve) is not bool:
        raise FeasibilityError("a remote ballot must be explicitly yes or no")
    for value, label in (
        (motion_id, "motion_id"), (voter_id, "voter_id"),
        (return_route_id, "return_route_id"), (cause, "cause"),
    ):
        _identifier(value, label)

    def change(world: Universe) -> dict[str, Any]:
        motion = _active_motion(world, motion_id)
        institution = world.institutions[motion.institution_id]
        actor = _remote_voter(world, motion_id, motion, institution, voter_id)
        digest = motion_fingerprint(motion)
        notices = [notice for notice in actor.received_reports
                   if _notice_matches(world, notice, motion_id, motion, digest)]
        if not notices:
            raise FeasibilityError("remote actor has not received a matching motion notice")
        route = _return_route(engine, world, actor, institution, return_route_id)
        energy = _send_signal_energy(world, route)
        due = world.time_s + _travel_seconds(route.distance_km, route.signal_speed_km_s)
        ballot_id = engine._id(world, "ballot")
        world.remote_ballots[ballot_id] = RemoteBallot(
            ballot_id=ballot_id, motion_id=motion_id, voter_id=voter_id,
            route_id=return_route_id, approve=approve,
            sent_s=world.time_s, arrives_s=due, notice_sha256=digest,
        )
        _schedule_signal(engine, world, route, "policy_ballot_arrival", {"ballot_id": ballot_id})
        return {
            "ballot_id": ballot_id, "motion_id": motion_id,
            "voter_id": voter_id, "route_id": return_route_id,
            "motion_sha256": digest,
            "ballot_intent_approve": approve,
            "sent_s": world.time_s, "arrival_s": due,
            "energy_to_heat_j": energy,
            "counted_by_institution": False,
            "voter_binding_sha256": _actor_binding(world, voter_id),
            "scope": "synthetic_L2_only",
        }

    return engine._commit("remote_ballot_sent", voter_id, cause, change)


def deliver_remote_ballot(world: Universe, ballot_id: str) -> dict[str, Any]:
    """Count only delivered, still-eligible member choices; close late arrivals."""
    ballot = world.remote_ballots[ballot_id]
    motion = world.relief_motions[ballot.motion_id]
    if ballot.status != "in_flight" or world.time_s != ballot.arrives_s:
        raise FeasibilityError("ballot delivery outside established causal time")
    if (motion.status != "proposed" or world.time_s >= motion.expires_s
            or ballot.voter_id in motion.votes
            or not ballot_eligible(world, motion, ballot.voter_id)):
        ballot.status = "arrived_unusable"
        reason = "expired_or_closed_motion"
        counted = False
    else:
        motion.votes[ballot.voter_id] = ballot.approve
        ballot.status = "counted"
        if unreachable_approval(world, motion):
            motion.status = "rejected"
        reason = "counted"
        counted = True
    return {
        "ballot_id": ballot.ballot_id, "motion_id": motion.motion_id,
        "voter_id": ballot.voter_id, "motion_sha256": ballot.notice_sha256,
        "ballot_intent_approve": ballot.approve,
        "sent_s": ballot.sent_s, "received_s": world.time_s,
        "counted_by_institution": counted, "delivery_outcome": reason,
        "motion_status": motion.status,
        "ballots_counted": len(motion.votes),
        "decision_protocol": protocol_label(world, motion.institution_id),
        "scope": "synthetic_L2_only",
    }


def distributed_council_view(engine: CausalEngine, institution_id: str) -> dict[str, Any]:
    """Read-only operator view; pending ballot *choices* stay undisclosed."""
    from .political_actions import institution_view

    base = institution_view(engine, institution_id)
    world = engine.state
    pending: dict[str, int] = {}
    for ballot in world.remote_ballots.values():
        if (world.relief_motions[ballot.motion_id].institution_id == institution_id
                and ballot.status == "in_flight"):
            pending[ballot.motion_id] = pending.get(ballot.motion_id, 0) + 1
    return {
        "schema": "gumas.unified.distributed_council_view.p5",
        "authority": "synthetic_operator_only_not_actor_knowledge",
        "institution": base,
        "in_flight_ballot_counts": pending,
        "pending_ballot_choices_visible_to_institution": False,
        "canon_authority": False,
    }
