"""P6 seatless synthetic association state and validation contracts.

This is L2 fixture-only. Institution formation requires a two-way physically
delivered invitation/consent. A member's association is not a site polity or
source-canon identity. No L1, L3, QGIA, tactical or registry authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any


def fingerprint(payload: dict[str, Any]) -> str:
    data = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                      allow_nan=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


@dataclass
class Charter:
    charter_id: str
    founder_id: str
    invitee_id: str
    purpose: str
    outbound_route_id: str
    offered_s: int
    offer_due_s: int
    expires_s: int
    terms_sha256: str
    status: str = "offer_inflight"
    return_route_id: str | None = None
    response_sent_s: int | None = None
    response_due_s: int | None = None
    response_accept: bool | None = None
    association_id: str | None = None


@dataclass
class Association:
    association_id: str
    charter_id: str
    members: tuple[str, str]
    formed_s: int
    charter_sha256: str
    authority: str = "synthetic_L2_only"
    confirmation_sent_s: int | None = None
    confirmation_due_s: int | None = None
    confirmed_to_invitee: bool = False


@dataclass
class Mandate:
    mandate_id: str
    association_id: str
    proposer_id: str
    voter_id: str
    custodian_id: str
    cargo_route_id: str
    outbound_route_id: str
    commodity: str
    amount: int
    offered_s: int
    offer_due_s: int
    expires_s: int
    terms_sha256: str
    status: str = "offer_inflight"
    return_route_id: str | None = None
    vote_sent_s: int | None = None
    vote_due_s: int | None = None
    vote_approve: bool | None = None
    authorized_at_s: int | None = None
    shipment_id: str | None = None
    shipment_departed_s: int | None = None
    shipment_due_s: int | None = None


@dataclass(frozen=True)
class MandateRequest:
    """Bounded P6 proposal terms without an overlong positional API."""
    cargo_route_id: str
    notice_route_id: str
    commodity: str
    amount: int
    expires_s: int


def charter_terms(charter: Charter) -> dict[str, Any]:
    return {
        "charter_id": charter.charter_id,
        "founder_id": charter.founder_id,
        "invitee_id": charter.invitee_id,
        "purpose": charter.purpose,
        "offered_s": charter.offered_s,
        "expires_s": charter.expires_s,
    }


def mandate_terms(mandate: Mandate) -> dict[str, Any]:
    return {
        "mandate_id": mandate.mandate_id,
        "association_id": mandate.association_id,
        "proposer_id": mandate.proposer_id,
        "voter_id": mandate.voter_id,
        "custodian_id": mandate.custodian_id,
        "cargo_route_id": mandate.cargo_route_id,
        "commodity": mandate.commodity,
        "amount": mandate.amount,
        "offered_s": mandate.offered_s,
        "expires_s": mandate.expires_s,
    }


def _nat(value: Any) -> bool:
    return type(value) is int and 0 <= value <= 10**15


def _sha(value: Any) -> bool:
    return (isinstance(value, str) and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def _event(world: Any, kind: str, field: str, item_id: str, due: int) -> bool:
    return any(
        x.kind == kind and x.payload.get(field) == item_id and x.due_s == due
        for x in world.pending
    )


def _path(world: Any, route_id: str, source: str, target: str,
          sent_s: int, due_s: int) -> bool:
    route = world.corridors.get(route_id)
    return (route is not None and route.origin_id == source
            and route.destination_id == target
            and _nat(sent_s) and _nat(due_s)
            and due_s == sent_s +
            (route.distance_km + route.signal_speed_km_s - 1)
            // route.signal_speed_km_s)


def _seen(actor: Any, kind: str, ref_id: str, digest: str,
          terms: dict[str, Any], at_or_before: int) -> bool:
    return any(
        x.get("kind") == kind and x.get("ref_id") == ref_id
        and x.get("terms_sha256") == digest and x.get("terms") == terms
        and _nat(x.get("received_s")) and x["received_s"] <= at_or_before
        for x in actor.received_reports
    )


def _charter_grounding(world: Any, key: str, charter: Charter):
    if not isinstance(charter, Charter) or key != charter.charter_id:
        raise ValueError("invalid seatless charter record")
    founder = world.actors.get(charter.founder_id)
    invitee = world.actors.get(charter.invitee_id)
    if founder is None or invitee is None:
        raise ValueError("charter has ungrounded actors, path or terms")
    if not isinstance(charter.purpose, str):
        raise ValueError("charter has ungrounded actors, path or terms")
    valid = (
        charter.founder_id != charter.invitee_id,
        0 < len(charter.purpose) <= 160,
        _nat(charter.offered_s),
        _nat(charter.expires_s),
        charter.expires_s > charter.offered_s,
        charter.offered_s <= world.time_s,
        _path(world, charter.outbound_route_id, founder.site_id,
              invitee.site_id, charter.offered_s, charter.offer_due_s),
        _sha(charter.terms_sha256),
        charter.terms_sha256 == fingerprint(charter_terms(charter)),
    )
    if not all(valid):
        raise ValueError("charter has ungrounded actors, path or terms")
    return founder, invitee


def _charter_offer_state(world: Any, key: str, charter: Charter,
                         invitee: Any) -> None:
    allowed = {"offer_inflight", "awaiting_response", "response_inflight",
               "formed", "declined", "expired"}
    if charter.status not in allowed:
        raise ValueError("invalid charter state")
    if charter.status == "offer_inflight":
        if not _event(world, "charter_offer_arrival", "charter_id",
                      key, charter.offer_due_s):
            raise ValueError("charter offer missing its scheduled transmission")
    informed = {"awaiting_response", "response_inflight", "formed", "declined"}
    if charter.status in informed:
        if not _seen(invitee, "seatless_charter_offer", key,
                     charter.terms_sha256, charter_terms(charter), world.time_s):
            raise ValueError("charter recipient lacks actually delivered terms")


def _charter_sent_intent(world: Any, charter: Charter,
                         founder: Any, invitee: Any) -> None:
    if type(charter.response_accept) is not bool:
        raise ValueError("charter response lacks physical informed intent")
    correct = (
        _path(world, charter.return_route_id, invitee.site_id, founder.site_id,
              charter.response_sent_s, charter.response_due_s),
        charter.response_sent_s >= charter.offer_due_s,
        charter.response_sent_s < charter.expires_s,
        _seen(invitee, "seatless_charter_offer", charter.charter_id,
              charter.terms_sha256, charter_terms(charter),
              charter.response_sent_s),
    )
    if not all(correct):
        raise ValueError("charter response lacks physical informed intent")


def _charter_response_fields(world: Any, charter: Charter,
                             founder: Any, invitee: Any) -> None:
    unopened = {"offer_inflight", "awaiting_response"}
    answered = {"response_inflight", "formed", "declined"}
    if charter.status in unopened and charter.response_sent_s is not None:
        raise ValueError("charter cannot have a response before transmission")
    if charter.status in answered and charter.response_sent_s is None:
        raise ValueError("charter decision requires recorded return transmission")
    if charter.response_sent_s is None:
        fields = (charter.return_route_id, charter.response_due_s,
                  charter.response_accept)
        if any(value is not None for value in fields):
            raise ValueError("charter response fields without sent intent")
        return
    _charter_sent_intent(world, charter, founder, invitee)


def _choice_delivered(actor: Any, kind: str, ref_id: str,
                      digest: str, terms: dict[str, Any],
                      decision: bool, time_s: int) -> bool:
    return any(
        all((
            entry.get("kind") == kind,
            entry.get("ref_id") == ref_id,
            entry.get("decision") is decision,
            entry.get("terms_sha256") == digest,
            entry.get("terms") == terms,
            entry.get("received_s") == time_s,
        ))
        for entry in actor.received_reports
    )


def _charter_receipt_state(world: Any, key: str, charter: Charter,
                           founder: Any) -> None:
    if charter.status == "response_inflight":
        if not _event(world, "charter_response_arrival", "charter_id",
                      key, charter.response_due_s):
            raise ValueError("in-flight charter response missing return event")
    if charter.status in {"formed", "declined"}:
        if not _choice_delivered(
            founder, "seatless_charter_response", key,
            charter.terms_sha256, charter_terms(charter),
            charter.response_accept, charter.response_due_s,
        ):
            raise ValueError("founder has not actually received the charter decision")


def _charter_terminal_state(charter: Charter) -> None:
    if charter.status == "formed":
        if not all((
            charter.association_id is not None,
            charter.response_accept is True,
            charter.response_due_s < charter.expires_s,
        )):
            raise ValueError("charter formed without timely affirmative receipt")
    elif charter.association_id is not None:
        raise ValueError("unformed charter cannot confer association authority")
    if charter.status == "declined" and charter.response_accept is not False:
        raise ValueError("declined charter must derive from explicit negative response")


def _validate_charter(world: Any, key: str, charter: Charter) -> None:
    founder, invitee = _charter_grounding(world, key, charter)
    _charter_offer_state(world, key, charter, invitee)
    _charter_response_fields(world, charter, founder, invitee)
    _charter_receipt_state(world, key, charter, founder)
    _charter_terminal_state(charter)


def _association_foundation(world: Any, key: str, association: Association):
    if not isinstance(association, Association) or key != association.association_id:
        raise ValueError("invalid association record")
    charter = world.charters.get(association.charter_id)
    if charter is None:
        raise ValueError("seatless association was not founded by received consent")
    valid = (
        charter.status == "formed",
        charter.association_id == key,
        association.members == (charter.founder_id, charter.invitee_id),
        association.charter_sha256 == charter.terms_sha256,
        association.authority == "synthetic_L2_only",
        _nat(association.formed_s),
        association.formed_s == charter.response_due_s,
        association.formed_s <= world.time_s,
    )
    if not all(valid):
        raise ValueError("seatless association was not founded by received consent")
    return charter


def _association_confirmation_delivery(world: Any, key: str,
                                       association: Association,
                                       charter: Charter) -> None:
    if association.confirmed_to_invitee:
        if not _seen(world.actors[charter.invitee_id],
                     "seatless_association_confirm", key,
                     charter.terms_sha256, charter_terms(charter), world.time_s):
            raise ValueError("remote member cannot know unreceived association")
    elif not _event(world, "association_confirm_arrival", "association_id",
                    key, association.confirmation_due_s):
        raise ValueError("association confirmation is not actually in transit")


def _association_confirmation(world: Any, key: str, association: Association,
                              charter: Charter) -> None:
    if association.confirmation_sent_s is None:
        if (association.confirmation_due_s is not None
                or association.confirmed_to_invitee is not False):
            raise ValueError("association has no physically sent formation confirmation")
        return
    path = _path(
        world, charter.outbound_route_id,
        world.actors[charter.founder_id].site_id,
        world.actors[charter.invitee_id].site_id,
        association.confirmation_sent_s, association.confirmation_due_s,
    )
    if association.confirmation_sent_s < association.formed_s or not path:
        raise ValueError("association confirmation lacks physical signal path")
    _association_confirmation_delivery(world, key, association, charter)


def _validate_association(world: Any, key: str, association: Association) -> None:
    charter = _association_foundation(world, key, association)
    _association_confirmation(world, key, association, charter)


def _mandate_participants(world: Any, key: str, mandate: Mandate):
    if not isinstance(mandate, Mandate) or key != mandate.mandate_id:
        raise ValueError("invalid association mandate")
    assoc = world.associations.get(mandate.association_id)
    if assoc is None:
        raise ValueError("mandate lacks distinct recorded association participants")
    if {mandate.proposer_id, mandate.voter_id} != set(assoc.members):
        raise ValueError("mandate lacks distinct recorded association participants")
    return assoc, world.actors[mandate.proposer_id], world.actors[mandate.voter_id]


def _mandate_grounding(world: Any, mandate: Mandate,
                       assoc: Association, proposer: Any, voter: Any) -> None:
    custodian = world.actors.get(mandate.custodian_id)
    route = world.corridors.get(mandate.cargo_route_id)
    if custodian is None or route is None:
        raise ValueError("mandate has invalid custody, physical path or terms")
    if not isinstance(mandate.commodity, str):
        raise ValueError("mandate has invalid custody, physical path or terms")
    valid = (
        mandate.custodian_id == mandate.proposer_id,
        route.origin_id == custodian.site_id,
        0 < len(mandate.commodity) <= 128,
        mandate.commodity != "energy_j",
        type(mandate.amount) is int,
        mandate.amount > 0,
        _nat(mandate.offered_s),
        mandate.offered_s >= assoc.formed_s,
        mandate.offered_s <= world.time_s,
        _nat(mandate.expires_s),
        mandate.expires_s > mandate.offered_s,
        _path(world, mandate.outbound_route_id, proposer.site_id,
              voter.site_id, mandate.offered_s, mandate.offer_due_s),
        _sha(mandate.terms_sha256),
        mandate.terms_sha256 == fingerprint(mandate_terms(mandate)),
    )
    if not all(valid):
        raise ValueError("mandate has invalid custody, physical path or terms")


def _mandate_offer_state(world: Any, key: str, mandate: Mandate,
                         voter: Any) -> None:
    allowed = {"offer_inflight", "awaiting_vote", "vote_inflight",
               "authorized", "rejected", "expired", "executed"}
    if mandate.status not in allowed:
        raise ValueError("invalid mandate state")
    if mandate.status == "offer_inflight":
        if not _event(world, "mandate_offer_arrival", "mandate_id",
                      key, mandate.offer_due_s):
            raise ValueError("mandate offer lacks scheduled path")
    informed = {"awaiting_vote", "vote_inflight", "authorized", "rejected",
                "executed"}
    if mandate.status in informed:
        if not _seen(voter, "seatless_mandate_offer", key,
                     mandate.terms_sha256, mandate_terms(mandate), world.time_s):
            raise ValueError("mandate voter lacks delivered terms")


def _mandate_sent_vote(world: Any, mandate: Mandate,
                       proposer: Any, voter: Any) -> None:
    correct = (
        type(mandate.vote_approve) is bool,
        _path(world, mandate.return_route_id, voter.site_id, proposer.site_id,
              mandate.vote_sent_s, mandate.vote_due_s),
        mandate.vote_sent_s >= mandate.offer_due_s,
        mandate.vote_sent_s < mandate.expires_s,
        _seen(voter, "seatless_mandate_offer", mandate.mandate_id,
              mandate.terms_sha256, mandate_terms(mandate),
              mandate.vote_sent_s),
    )
    if not all(correct):
        raise ValueError("mandate vote lacks physically informed actor")


def _mandate_vote_fields(world: Any, mandate: Mandate,
                         proposer: Any, voter: Any) -> None:
    unopened = {"offer_inflight", "awaiting_vote"}
    answered = {"vote_inflight", "authorized", "rejected", "executed"}
    if mandate.status in unopened and mandate.vote_sent_s is not None:
        raise ValueError("mandate cannot contain unsent or prematurely counted vote")
    if mandate.status in answered and mandate.vote_sent_s is None:
        raise ValueError("mandate requires recorded vote transmission")
    if mandate.vote_sent_s is None:
        fields = (mandate.return_route_id, mandate.vote_due_s,
                  mandate.vote_approve)
        if any(x is not None for x in fields):
            raise ValueError("mandate voting fields without intent")
        return
    _mandate_sent_vote(world, mandate, proposer, voter)


def _mandate_receipt_state(world: Any, key: str, mandate: Mandate,
                           proposer: Any) -> None:
    if mandate.status == "vote_inflight":
        if not _event(world, "mandate_vote_arrival", "mandate_id",
                      key, mandate.vote_due_s):
            raise ValueError("mandate vote has no causal return event")
    if mandate.status in {"authorized", "executed", "rejected"}:
        if not _choice_delivered(
            proposer, "seatless_mandate_response", key,
            mandate.terms_sha256, mandate_terms(mandate),
            mandate.vote_approve, mandate.vote_due_s,
        ):
            raise ValueError("mandate coordinator lacks physically received decision")


def _mandate_authority_state(mandate: Mandate) -> None:
    if mandate.status in {"authorized", "executed"}:
        valid = (
            mandate.vote_approve is True,
            mandate.authorized_at_s == mandate.vote_due_s,
            mandate.vote_due_s < mandate.expires_s,
        )
        if not all(valid):
            raise ValueError("authorized mandate lacks timely affirmative vote")
    elif mandate.authorized_at_s is not None:
        raise ValueError("unapproved mandate has approval timestamp")
    if mandate.status == "rejected" and mandate.vote_approve is not False:
        raise ValueError("rejected mandate must derive from negative consent")


def _validate_mandate(world: Any, key: str, mandate: Mandate) -> None:
    assoc, proposer, voter = _mandate_participants(world, key, mandate)
    _mandate_grounding(world, mandate, assoc, proposer, voter)
    _mandate_offer_state(world, key, mandate, voter)
    _mandate_vote_fields(world, mandate, proposer, voter)
    _mandate_receipt_state(world, key, mandate, proposer)
    _mandate_authority_state(mandate)
    from .federated_shipment import validate_executed_shipment

    validate_executed_shipment(world, mandate)


_CHARTER_EVENTS = {
    "charter_offer_arrival": "offer_due_s",
    "charter_response_arrival": "response_due_s",
    "charter_expiry": "expires_s",
}
_MANDATE_EVENTS = {
    "mandate_offer_arrival": "offer_due_s",
    "mandate_vote_arrival": "vote_due_s",
    "mandate_expiry": "expires_s",
}


def _validate_charter_scheduler_event(world: Any, event: Any) -> None:
    charter = world.charters.get(event.payload.get("charter_id"))
    if charter is None:
        raise ValueError("orphaned charter scheduler event")
    if event.due_s != getattr(charter, _CHARTER_EVENTS[event.kind]):
        raise ValueError("charter scheduler time mismatches contract")


def _validate_mandate_scheduler_event(world: Any, event: Any) -> None:
    mandate = world.mandates.get(event.payload.get("mandate_id"))
    if mandate is None:
        raise ValueError("orphaned mandate scheduler event")
    if event.due_s != getattr(mandate, _MANDATE_EVENTS[event.kind]):
        raise ValueError("mandate scheduler time mismatches contract")


def _validate_confirmation_scheduler_event(world: Any, event: Any) -> None:
    assoc = world.associations.get(event.payload.get("association_id"))
    if assoc is None:
        raise ValueError("orphaned association confirmation signal")
    if assoc.confirmed_to_invitee or assoc.confirmation_due_s != event.due_s:
        raise ValueError("orphaned association confirmation signal")


def _validate_federated_scheduler_event(world: Any, event: Any) -> None:
    if event.kind in _CHARTER_EVENTS:
        _validate_charter_scheduler_event(world, event)
    elif event.kind in _MANDATE_EVENTS:
        _validate_mandate_scheduler_event(world, event)
    elif event.kind == "association_confirm_arrival":
        _validate_confirmation_scheduler_event(world, event)


def validate_federated_world(world: Any) -> None:
    """P0 proof obligations for seatless P6 organizations and scheduled facts."""
    if any(len(records) > 128 for records in (
        world.charters, world.associations, world.mandates
    )):
        raise ValueError("synthetic federation fixture exceeds bounded scope")
    for key, charter in world.charters.items():
        _validate_charter(world, key, charter)
    for key, association in world.associations.items():
        _validate_association(world, key, association)
    for key, mandate in world.mandates.items():
        _validate_mandate(world, key, mandate)
    for event in world.pending:
        _validate_federated_scheduler_event(world, event)
