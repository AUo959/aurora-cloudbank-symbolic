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


def _validate_charter(world: Any, key: str, charter: Charter) -> None:
    if not isinstance(charter, Charter) or key != charter.charter_id:
        raise ValueError("invalid seatless charter record")
    founder = world.actors.get(charter.founder_id)
    invitee = world.actors.get(charter.invitee_id)
    if (founder is None or invitee is None or founder == invitee
            or not isinstance(charter.purpose, str)
            or not 0 < len(charter.purpose) <= 160
            or not _nat(charter.offered_s)
            or not _nat(charter.expires_s)
            or charter.expires_s <= charter.offered_s
            or charter.offered_s > world.time_s
            or not _path(world, charter.outbound_route_id,
                         founder.site_id, invitee.site_id,
                         charter.offered_s, charter.offer_due_s)
            or not _sha(charter.terms_sha256)
            or charter.terms_sha256 != fingerprint(charter_terms(charter))):
        raise ValueError("charter has ungrounded actors, path or terms")
    allowed = {"offer_inflight", "awaiting_response", "response_inflight",
               "formed", "declined", "expired"}
    if charter.status not in allowed:
        raise ValueError("invalid charter state")
    if (charter.status == "offer_inflight"
            and not _event(world, "charter_offer_arrival", "charter_id", key,
                           charter.offer_due_s)):
        raise ValueError("charter offer missing its scheduled transmission")
    if charter.status in {"awaiting_response", "response_inflight", "formed", "declined"}:
        if not _seen(invitee, "seatless_charter_offer", key,
                     charter.terms_sha256, charter_terms(charter), world.time_s):
            raise ValueError("charter recipient lacks actually delivered terms")
    if charter.response_sent_s is None:
        if (charter.return_route_id is not None
                or charter.response_due_s is not None
                or charter.response_accept is not None):
            raise ValueError("charter response fields without sent intent")
    else:
        if (type(charter.response_accept) is not bool
                or not _path(world, charter.return_route_id,
                             invitee.site_id, founder.site_id,
                             charter.response_sent_s, charter.response_due_s)
                or charter.response_sent_s < charter.offer_due_s
                or charter.response_sent_s >= charter.expires_s
                or not _seen(invitee, "seatless_charter_offer", key,
                             charter.terms_sha256, charter_terms(charter),
                             charter.response_sent_s)):
            raise ValueError("charter response lacks physical informed intent")
    if (charter.status == "response_inflight"
            and not _event(world, "charter_response_arrival", "charter_id", key,
                           charter.response_due_s)):
        raise ValueError("in-flight charter response missing return event")
    if charter.status in {"formed", "declined"}:
        if not any(
            r.get("kind") == "seatless_charter_response"
            and r.get("ref_id") == key
            and r.get("decision") is charter.response_accept
            and r.get("terms_sha256") == charter.terms_sha256
            and r.get("terms") == charter_terms(charter)
            and r.get("received_s") == charter.response_due_s
            for r in founder.received_reports
        ):
            raise ValueError("founder has not actually received the charter decision")
    if charter.status == "formed":
        if (charter.association_id is None
                or charter.response_accept is not True
                or charter.response_due_s >= charter.expires_s):
            raise ValueError("charter formed without timely affirmative receipt")
    elif charter.association_id is not None:
        raise ValueError("unformed charter cannot confer association authority")
    if charter.status == "declined" and charter.response_accept is not False:
        raise ValueError("declined charter must derive from explicit negative response")


def _validate_association(world: Any, key: str, association: Association) -> None:
    if not isinstance(association, Association) or key != association.association_id:
        raise ValueError("invalid association record")
    charter = world.charters.get(association.charter_id)
    if (charter is None or charter.status != "formed"
            or charter.association_id != key
            or association.members != (charter.founder_id, charter.invitee_id)
            or association.charter_sha256 != charter.terms_sha256
            or association.authority != "synthetic_L2_only"
            or not _nat(association.formed_s)
            or association.formed_s != charter.response_due_s
            or association.formed_s > world.time_s):
        raise ValueError("seatless association was not founded by received consent")
    if association.confirmation_sent_s is None:
        if (association.confirmation_due_s is not None
                or association.confirmed_to_invitee is not False):
            raise ValueError("association has no physically sent formation confirmation")
    else:
        if (association.confirmation_sent_s < association.formed_s
                or not _path(world, charter.outbound_route_id,
                             world.actors[charter.founder_id].site_id,
                             world.actors[charter.invitee_id].site_id,
                             association.confirmation_sent_s,
                             association.confirmation_due_s)):
            raise ValueError("association confirmation lacks physical signal path")
        if association.confirmed_to_invitee:
            if not _seen(world.actors[charter.invitee_id],
                         "seatless_association_confirm", key,
                         charter.terms_sha256, charter_terms(charter),
                         world.time_s):
                raise ValueError("remote member cannot know unreceived association")
        elif not _event(world, "association_confirm_arrival", "association_id",
                        key, association.confirmation_due_s):
            raise ValueError("association confirmation is not actually in transit")


def _validate_mandate(world: Any, key: str, mandate: Mandate) -> None:
    if not isinstance(mandate, Mandate) or key != mandate.mandate_id:
        raise ValueError("invalid association mandate")
    association = world.associations.get(mandate.association_id)
    if association is None or {mandate.proposer_id, mandate.voter_id} != set(association.members):
        raise ValueError("mandate lacks distinct recorded association participants")
    proposer = world.actors[mandate.proposer_id]
    voter = world.actors[mandate.voter_id]
    custodian = world.actors.get(mandate.custodian_id)
    route = world.corridors.get(mandate.cargo_route_id)
    if (custodian is None or mandate.custodian_id != mandate.proposer_id
            or route is None or route.origin_id != custodian.site_id
            or not isinstance(mandate.commodity, str)
            or not 0 < len(mandate.commodity) <= 128
            or mandate.commodity == "energy_j"
            or type(mandate.amount) is not int or mandate.amount <= 0
            or not _nat(mandate.offered_s)
            or mandate.offered_s < association.formed_s
            or mandate.offered_s > world.time_s
            or not _nat(mandate.expires_s)
            or mandate.expires_s <= mandate.offered_s
            or not _path(world, mandate.outbound_route_id,
                         proposer.site_id, voter.site_id,
                         mandate.offered_s, mandate.offer_due_s)
            or not _sha(mandate.terms_sha256)
            or mandate.terms_sha256 != fingerprint(mandate_terms(mandate))):
        raise ValueError("mandate has invalid custody, physical path or terms")
    if mandate.status not in {"offer_inflight", "awaiting_vote", "vote_inflight",
                              "authorized", "rejected", "expired", "executed"}:
        raise ValueError("invalid mandate state")
    if (mandate.status == "offer_inflight"
            and not _event(world, "mandate_offer_arrival", "mandate_id", key,
                           mandate.offer_due_s)):
        raise ValueError("mandate offer lacks scheduled path")
    if mandate.status in {"awaiting_vote", "vote_inflight", "authorized", "rejected", "executed"}:
        if not _seen(voter, "seatless_mandate_offer", key,
                     mandate.terms_sha256, mandate_terms(mandate), world.time_s):
            raise ValueError("mandate voter lacks delivered terms")
    if mandate.vote_sent_s is None:
        if (mandate.return_route_id is not None
                or mandate.vote_due_s is not None
                or mandate.vote_approve is not None):
            raise ValueError("mandate voting fields without intent")
    elif (type(mandate.vote_approve) is not bool
          or not _path(world, mandate.return_route_id,
                       voter.site_id, proposer.site_id,
                       mandate.vote_sent_s, mandate.vote_due_s)
          or mandate.vote_sent_s < mandate.offer_due_s
          or mandate.vote_sent_s >= mandate.expires_s
          or not _seen(voter, "seatless_mandate_offer", key,
                       mandate.terms_sha256, mandate_terms(mandate),
                       mandate.vote_sent_s)):
        raise ValueError("mandate vote lacks physically informed actor")
    if (mandate.status == "vote_inflight"
            and not _event(world, "mandate_vote_arrival", "mandate_id", key,
                           mandate.vote_due_s)):
        raise ValueError("mandate vote has no causal return event")
    if mandate.status in {"authorized", "executed", "rejected"}:
        if not any(
            r.get("kind") == "seatless_mandate_response"
            and r.get("ref_id") == key
            and r.get("decision") is mandate.vote_approve
            and r.get("terms_sha256") == mandate.terms_sha256
            and r.get("terms") == mandate_terms(mandate)
            and r.get("received_s") == mandate.vote_due_s
            for r in proposer.received_reports
        ):
            raise ValueError("mandate coordinator lacks physically received decision")
    if mandate.status in {"authorized", "executed"}:
        if (mandate.vote_approve is not True
                or mandate.authorized_at_s != mandate.vote_due_s
                or mandate.vote_due_s >= mandate.expires_s):
            raise ValueError("authorized mandate lacks timely affirmative vote")
    elif mandate.authorized_at_s is not None:
        raise ValueError("unapproved mandate has approval timestamp")
    if (mandate.status == "executed") != (mandate.shipment_id is not None):
        raise ValueError("mandate shipment/status mismatch")
    if mandate.shipment_id is not None:
        if not any(e.kind == "cargo_arrival"
                   and e.payload.get("shipment_id") == mandate.shipment_id
                   for e in world.pending) and mandate.shipment_id not in world.in_transit:
            # A completed shipment need not remain in transit. The terminal
            # mandate receipt persists; P0's ledger supplies its history.
            if world.time_s < mandate.authorized_at_s:
                raise ValueError("executed mandate precedes authorization")


def validate_federated_world(world: Any) -> None:
    """Post-P0 validation. Never infer a new polity from an association name."""
    if (len(world.charters) > 128 or len(world.associations) > 128
            or len(world.mandates) > 128):
        raise ValueError("synthetic federation fixture exceeds bounded scope")
    for key, charter in world.charters.items():
        _validate_charter(world, key, charter)
    for key, association in world.associations.items():
        _validate_association(world, key, association)
    for key, mandate in world.mandates.items():
        _validate_mandate(world, key, mandate)
    for event in world.pending:
        if event.kind in {"charter_offer_arrival", "charter_response_arrival",
                          "charter_expiry"}:
            charter = world.charters.get(event.payload.get("charter_id"))
            if charter is None:
                raise ValueError("orphaned charter scheduler event")
            allowed = {
                "charter_offer_arrival": charter.offer_due_s,
                "charter_response_arrival": charter.response_due_s,
                "charter_expiry": charter.expires_s,
            }
            if event.due_s != allowed[event.kind]:
                raise ValueError("charter scheduler time mismatches contract")
        if event.kind == "association_confirm_arrival":
            association = world.associations.get(event.payload.get("association_id"))
            if (association is None or association.confirmed_to_invitee
                    or association.confirmation_due_s != event.due_s):
                raise ValueError("orphaned association confirmation signal")
        if event.kind in {"mandate_offer_arrival", "mandate_vote_arrival",
                          "mandate_expiry"}:
            mandate = world.mandates.get(event.payload.get("mandate_id"))
            if mandate is None:
                raise ValueError("orphaned mandate scheduler event")
            allowed = {
                "mandate_offer_arrival": mandate.offer_due_s,
                "mandate_vote_arrival": mandate.vote_due_s,
                "mandate_expiry": mandate.expires_s,
            }
            if event.due_s != allowed[event.kind]:
                raise ValueError("mandate scheduler time mismatches contract")
