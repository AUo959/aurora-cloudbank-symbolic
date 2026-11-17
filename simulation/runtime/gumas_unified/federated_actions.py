"""P6: seatless two-member charters and mandate execution in synthetic L2.

A charter is offered over a directed signal, explicitly accepted by another
individual, and founded only when the return decision arrives. The founder
may then explicitly confirm formation to the remote participant. Either
informed member can coordinate a new two-party mandate from their own site;
a separate physical custodian must execute an authorized, feasible transfer.
No automatic canon, L1/L3 actions, new polity or general political teleology.
"""
from __future__ import annotations

from typing import Any

from .federated_model import (
    Association, Charter, Mandate, charter_terms, fingerprint, mandate_terms,
)
from .kernel import CausalEngine, FeasibilityError, Receipt, _travel_seconds
from .model import ScheduledEvent, Universe
from .federated_shipment import dispatch_mandate_shipment


def _bounded(value: Any, name: str, limit: int = 128) -> str:
    if not isinstance(value, str) or not 0 < len(value) <= limit or not value.strip():
        raise FeasibilityError(f"{name} must be a bounded nonempty string")
    return value


def _future(world: Universe, expires_s: int, earliest: int) -> None:
    if (type(expires_s) is not int
            or expires_s <= world.time_s or expires_s <= earliest
            or expires_s > 10**15):
        raise FeasibilityError("proposal expiry must allow physical notice delivery")


def _route(engine: CausalEngine, world: Universe, route_id: str,
           origin_actor_id: str, target_actor_id: str):
    route = engine._route(world, route_id)
    if origin_actor_id not in world.actors or target_actor_id not in world.actors:
        raise FeasibilityError("signal participants must be existing actors")
    if (route.origin_id != world.actors[origin_actor_id].site_id
            or route.destination_id != world.actors[target_actor_id].site_id
            or origin_actor_id == target_actor_id):
        raise FeasibilityError("no directed physical information route between participants")
    return route


def _signal(world: Universe, route) -> tuple[int, int]:
    energy = route.distance_km * route.signal_energy_j_per_km
    site = world.sites[route.origin_id]
    if site.inventory.get("energy_j", 0) < energy:
        raise FeasibilityError("insufficient energy for consent signal")
    site.inventory["energy_j"] -= energy
    world.heat_j += energy
    return world.time_s + _travel_seconds(
        route.distance_km, route.signal_speed_km_s), energy


def _schedule(engine: CausalEngine, world: Universe, kind: str, due_s: int,
              ref_field: str, ref: str) -> None:
    identifier = engine._id(world, "scheduled")
    world.pending.append(ScheduledEvent(
        identifier, due_s, world.next_serial, kind, {ref_field: ref}))


def _received(actor, kind: str, ref: str, digest: str,
              terms: dict[str, Any], now_s: int) -> bool:
    return any(
        r.get("kind") == kind and r.get("ref_id") == ref
        and r.get("terms_sha256") == digest and r.get("terms") == terms
        and type(r.get("received_s")) is int and r["received_s"] <= now_s
        for r in actor.received_reports
    )


def offer_charter(engine: CausalEngine, founder_id: str, invitee_id: str,
                  purpose: str, outbound_route_id: str, *,
                  expires_s: int, cause: str) -> Receipt:
    for v, name in ((founder_id, "founder"), (invitee_id, "invitee"),
                    (purpose, "purpose"), (outbound_route_id, "route"),
                    (cause, "cause")):
        _bounded(v, name, 160 if name == "purpose" else 128)
    if not isinstance(engine, CausalEngine) or not engine.run_id.startswith("synthetic-"):
        raise FeasibilityError("charters are synthetic L2 only")

    def change(world: Universe) -> dict[str, Any]:
        route = _route(engine, world, outbound_route_id, founder_id, invitee_id)
        due = world.time_s + _travel_seconds(
            route.distance_km, route.signal_speed_km_s)
        _future(world, expires_s, due)
        for a in world.associations.values():
            if set(a.members) == {founder_id, invitee_id}:
                raise FeasibilityError("these individuals already share an active charter")
        for c in world.charters.values():
            if ({c.founder_id, c.invitee_id} == {founder_id, invitee_id}
                    and c.status in {"offer_inflight", "awaiting_response", "response_inflight"}):
                raise FeasibilityError("existing pending charter requires a decision")
        due, energy = _signal(world, route)
        cid = engine._id(world, "charter")
        record = Charter(cid, founder_id, invitee_id, purpose,
                         outbound_route_id, world.time_s, due, expires_s, "")
        record.terms_sha256 = fingerprint(charter_terms(record))
        world.charters[cid] = record
        _schedule(engine, world, "charter_offer_arrival", due, "charter_id", cid)
        _schedule(engine, world, "charter_expiry", expires_s, "charter_id", cid)
        return {
            "charter_id": cid, "terms_sha256": record.terms_sha256,
            "founder_id": founder_id, "invitee_id": invitee_id,
            "notice_due_s": due, "expires_s": expires_s,
            "energy_to_heat_j": energy, "association_formed": False,
            "authority": "synthetic_L2_only",
        }
    return engine._commit("seatless_charter_offered", founder_id, cause, change)


def respond_charter(engine: CausalEngine, charter_id: str, invitee_id: str,
                    accept: bool, return_route_id: str, *, cause: str) -> Receipt:
    if type(accept) is not bool:
        raise FeasibilityError("charter consent must be explicit yes or no")
    for v, n in ((charter_id, "charter_id"), (invitee_id, "invitee"),
                 (return_route_id, "return_route"), (cause, "cause")):
        _bounded(v, n)

    def change(world: Universe) -> dict[str, Any]:
        charter = world.charters.get(charter_id)
        if (charter is None or charter.status != "awaiting_response"
                or invitee_id != charter.invitee_id
                or world.time_s >= charter.expires_s):
            raise FeasibilityError("charter cannot accept this response")
        recipient = world.actors[invitee_id]
        if not _received(recipient, "seatless_charter_offer",
                         charter_id, charter.terms_sha256,
                         charter_terms(charter), world.time_s):
            raise FeasibilityError("invitee has not received the actual charter terms")
        route = _route(engine, world, return_route_id,
                       invitee_id, charter.founder_id)
        due, energy = _signal(world, route)
        charter.return_route_id = return_route_id
        charter.response_sent_s = world.time_s
        charter.response_due_s = due
        charter.response_accept = accept
        charter.status = "response_inflight"
        _schedule(engine, world, "charter_response_arrival",
                  due, "charter_id", charter_id)
        return {
            "charter_id": charter_id, "invitee_id": invitee_id,
            "accept_intent": accept, "response_due_s": due,
            "counted_by_founder": False, "energy_to_heat_j": energy,
            "authority": "synthetic_L2_only",
        }
    return engine._commit("seatless_charter_response_sent",
                          invitee_id, cause, change)


def confirm_association(engine: CausalEngine, association_id: str,
                        founder_id: str, *, cause: str) -> Receipt:
    for v, n in ((association_id, "association_id"),
                 (founder_id, "founder"), (cause, "cause")):
        _bounded(v, n)

    def change(world: Universe) -> dict[str, Any]:
        assoc = world.associations.get(association_id)
        if assoc is None:
            raise FeasibilityError("association is not founded by received consent")
        charter = world.charters[assoc.charter_id]
        if founder_id != charter.founder_id:
            raise FeasibilityError("only the knowing founder can confirm formation")
        if assoc.confirmation_sent_s is not None:
            raise FeasibilityError("formation confirmation was already transmitted")
        route = _route(engine, world, charter.outbound_route_id,
                       charter.founder_id, charter.invitee_id)
        due, energy = _signal(world, route)
        assoc.confirmation_sent_s = world.time_s
        assoc.confirmation_due_s = due
        _schedule(engine, world, "association_confirm_arrival",
                  due, "association_id", association_id)
        return {
            "association_id": association_id, "founder_id": founder_id,
            "confirmation_due_s": due,
            "remote_member_knows_formation": False,
            "energy_to_heat_j": energy, "authority": "synthetic_L2_only",
        }
    return engine._commit("seatless_formation_confirm_sent",
                          founder_id, cause, change)


def _association_for_member(world: Universe, association_id: str,
                            proposer_id: str) -> tuple[Association, str]:
    association = world.associations.get(association_id)
    if association is None or proposer_id not in association.members:
        raise FeasibilityError("actor lacks formed association membership")
    charter = world.charters[association.charter_id]
    if proposer_id == charter.invitee_id and not association.confirmed_to_invitee:
        raise FeasibilityError("remote member has not received formation confirmation")
    other = (association.members[1] if association.members[0] == proposer_id
             else association.members[0])
    return association, other


def propose_mandate(engine: CausalEngine, association_id: str, proposer_id: str,
                    cargo_route_id: str, notice_route_id: str,
                    commodity: str, amount: int, *,
                    expires_s: int, cause: str) -> Receipt:
    for v, n in ((association_id, "association_id"), (proposer_id, "proposer"),
                 (cargo_route_id, "cargo route"), (notice_route_id, "notice route"),
                 (commodity, "commodity"), (cause, "cause")):
        _bounded(v, n)
    if commodity == "energy_j" or type(amount) is not int or not 0 < amount <= 10**12:
        raise FeasibilityError("mandate requires a positive physical commodity quantity")

    def change(world: Universe) -> dict[str, Any]:
        assoc, peer = _association_for_member(world, association_id, proposer_id)
        route = _route(engine, world, notice_route_id, proposer_id, peer)
        cargo = engine._route(world, cargo_route_id)
        if cargo.origin_id != world.actors[proposer_id].site_id:
            raise FeasibilityError("mandate custodian must physically control source site")
        due = world.time_s + _travel_seconds(
            route.distance_km, route.signal_speed_km_s)
        _future(world, expires_s, due)
        for m in world.mandates.values():
            if (m.association_id == association_id
                    and m.status in {"offer_inflight", "awaiting_vote",
                                     "vote_inflight", "authorized"}):
                raise FeasibilityError("association has an unresolved prior mandate")
        due, energy = _signal(world, route)
        mid = engine._id(world, "mandate")
        mandate = Mandate(
            mid, association_id, proposer_id, peer, proposer_id,
            cargo_route_id, notice_route_id, commodity, amount,
            world.time_s, due, expires_s, "")
        mandate.terms_sha256 = fingerprint(mandate_terms(mandate))
        world.mandates[mid] = mandate
        _schedule(engine, world, "mandate_offer_arrival", due, "mandate_id", mid)
        _schedule(engine, world, "mandate_expiry", expires_s, "mandate_id", mid)
        return {
            "mandate_id": mid, "association_id": assoc.association_id,
            "proposer_id": proposer_id, "peer_id": peer,
            "terms_sha256": mandate.terms_sha256,
            "notice_due_s": due, "expires_s": expires_s,
            "energy_to_heat_j": energy,
            "material_authorized": False, "authority": "synthetic_L2_only",
        }
    return engine._commit("seatless_mandate_offered", proposer_id, cause, change)


def respond_mandate(engine: CausalEngine, mandate_id: str, voter_id: str,
                    approve: bool, return_route_id: str, *, cause: str) -> Receipt:
    if type(approve) is not bool:
        raise FeasibilityError("mandate response must be a Boolean personal choice")
    for v, n in ((mandate_id, "mandate"), (voter_id, "voter"),
                 (return_route_id, "return_route"), (cause, "cause")):
        _bounded(v, n)

    def change(world: Universe) -> dict[str, Any]:
        mandate = world.mandates.get(mandate_id)
        if (mandate is None or mandate.status != "awaiting_vote"
                or mandate.voter_id != voter_id
                or world.time_s >= mandate.expires_s):
            raise FeasibilityError("mandate cannot accept this remote decision")
        actor = world.actors[voter_id]
        if not _received(actor, "seatless_mandate_offer", mandate_id,
                         mandate.terms_sha256, mandate_terms(mandate),
                         world.time_s):
            raise FeasibilityError("voter lacks delivered, verified mandate terms")
        route = _route(engine, world, return_route_id,
                       voter_id, mandate.proposer_id)
        due, energy = _signal(world, route)
        mandate.return_route_id = return_route_id
        mandate.vote_sent_s = world.time_s
        mandate.vote_due_s = due
        mandate.vote_approve = approve
        mandate.status = "vote_inflight"
        _schedule(engine, world, "mandate_vote_arrival",
                  due, "mandate_id", mandate_id)
        return {
            "mandate_id": mandate_id, "voter_id": voter_id,
            "vote_intent_approve": approve, "counted_by_coordinator": False,
            "vote_due_s": due, "energy_to_heat_j": energy,
            "authority": "synthetic_L2_only",
        }
    return engine._commit("seatless_mandate_vote_sent", voter_id, cause, change)


def execute_mandate(engine: CausalEngine, mandate_id: str,
                    custodian_id: str, *, cause: str) -> Receipt:
    _bounded(mandate_id, "mandate")
    _bounded(custodian_id, "custodian")
    _bounded(cause, "cause")

    def change(world: Universe) -> dict[str, Any]:
        mandate = world.mandates.get(mandate_id)
        if (mandate is None or mandate.status != "authorized"
                or mandate.custodian_id != custodian_id
                or world.time_s >= mandate.expires_s):
            raise FeasibilityError("mandate is not an active physical dispatch authority")
        assoc, _ = _association_for_member(world, mandate.association_id,
                                           custodian_id)
        material = dispatch_mandate_shipment(
            engine, world, mandate, custodian_id)
        return {
            "mandate_id": mandate_id, "association_id": assoc.association_id,
            "custodian_id": custodian_id,
            **material,
        }
    return engine._commit("seatless_mandate_dispatched",
                          custodian_id, cause, change)


def _report(world: Universe, actor_id: str, kind: str,
            ref_id: str, digest: str, terms: dict[str, Any],
            decision: bool | None = None) -> None:
    actor = world.actors[actor_id]
    record = {
        "kind": kind, "ref_id": ref_id, "terms_sha256": digest,
        "terms": dict(terms), "received_s": world.time_s,
    }
    if decision is not None:
        record["decision"] = decision
    actor.received_reports.append(record)


def _charter_event(world: Universe, kind: str, charter_id: str) -> dict[str, Any]:
    charter = world.charters[charter_id]
    result: dict[str, Any] = {"charter_id": charter_id, "time_s": world.time_s}
    if kind == "charter_offer_arrival":
        if charter.status == "offer_inflight" and world.time_s < charter.expires_s:
            charter.status = "awaiting_response"
            _report(world, charter.invitee_id, "seatless_charter_offer",
                    charter_id, charter.terms_sha256, charter_terms(charter))
            result["invitee_informed"] = True
        else:
            result["invitee_informed"] = False
    elif kind == "charter_response_arrival":
        if charter.status == "response_inflight" and world.time_s < charter.expires_s:
            _report(world, charter.founder_id, "seatless_charter_response",
                    charter_id, charter.terms_sha256, charter_terms(charter),
                    charter.response_accept)
            if charter.response_accept:
                aid = f"association-{charter.charter_id}"
                world.associations[aid] = Association(
                    aid, charter_id, (charter.founder_id, charter.invitee_id),
                    world.time_s, charter.terms_sha256)
                charter.association_id = aid
                charter.status = "formed"
                result["association_id"] = aid
            else:
                charter.status = "declined"
            result["response_counted"] = True
        else:
            result["response_counted"] = False
    elif kind == "charter_expiry":
        prior = charter.status
        if prior in {"offer_inflight", "awaiting_response", "response_inflight"}:
            charter.status = "expired"
        result["previous_status"] = prior
    result["status"] = charter.status
    return result


def _mandate_event(world: Universe, kind: str, mandate_id: str) -> dict[str, Any]:
    mandate = world.mandates[mandate_id]
    result: dict[str, Any] = {"mandate_id": mandate_id, "time_s": world.time_s}
    if kind == "mandate_offer_arrival":
        if mandate.status == "offer_inflight" and world.time_s < mandate.expires_s:
            mandate.status = "awaiting_vote"
            _report(world, mandate.voter_id, "seatless_mandate_offer",
                    mandate_id, mandate.terms_sha256, mandate_terms(mandate))
            result["peer_informed"] = True
        else:
            result["peer_informed"] = False
    elif kind == "mandate_vote_arrival":
        if mandate.status == "vote_inflight" and world.time_s < mandate.expires_s:
            _report(world, mandate.proposer_id, "seatless_mandate_response",
                    mandate_id, mandate.terms_sha256, mandate_terms(mandate),
                    mandate.vote_approve)
            mandate.status = "authorized" if mandate.vote_approve else "rejected"
            if mandate.vote_approve:
                mandate.authorized_at_s = world.time_s
            result["decision_counted"] = True
        else:
            result["decision_counted"] = False
    elif kind == "mandate_expiry":
        prior = mandate.status
        if prior in {"offer_inflight", "awaiting_vote",
                     "vote_inflight", "authorized"}:
            mandate.status = "expired"
            mandate.authorized_at_s = None
        result["previous_status"] = prior
    result["status"] = mandate.status
    return result


def deliver_federated_event(world: Universe, kind: str,
                            payload: dict[str, Any]) -> dict[str, Any]:
    """P0 scheduler only; event validity and times are checked by Universe."""
    if kind in {"charter_offer_arrival", "charter_response_arrival", "charter_expiry"}:
        return _charter_event(world, kind, payload["charter_id"])
    if kind == "association_confirm_arrival":
        assoc = world.associations[payload["association_id"]]
        charter = world.charters[assoc.charter_id]
        assoc.confirmed_to_invitee = True
        _report(world, charter.invitee_id, "seatless_association_confirm",
                assoc.association_id, charter.terms_sha256, charter_terms(charter))
        return {
            "association_id": assoc.association_id,
            "confirmed_to_invitee_at_s": world.time_s,
            "authority": "synthetic_L2_only",
        }
    if kind in {"mandate_offer_arrival", "mandate_vote_arrival", "mandate_expiry"}:
        return _mandate_event(world, kind, payload["mandate_id"])
    raise AssertionError("unsupported federated event")


def association_view(engine: CausalEngine, association_id: str) -> dict[str, Any]:
    """Review-only projection; never transmit this omniscient operator packet."""
    world = engine.state
    assoc = world.associations.get(association_id)
    if assoc is None:
        raise FeasibilityError("unknown formed association")
    return {
        "schema": "gumas.unified.seatless_association_view.p6",
        "authority": "synthetic_operator_only_not_actor_knowledge",
        "association_id": assoc.association_id,
        "members": list(assoc.members),
        "permanent_seat": None,
        "member_sites": {a: world.actors[a].site_id for a in assoc.members},
        "member_polity_labels": {
            a: world.sites[world.actors[a].site_id].polity_id for a in assoc.members
        },
        "formed_at_s": assoc.formed_s,
        "remote_member_received_confirmation": assoc.confirmed_to_invitee,
        "mandates": {
            mid: {"status": m.status, "proposer_id": m.proposer_id,
                  "amount": m.amount, "commodity": m.commodity,
                  "authorized_at_s": m.authorized_at_s}
            for mid, m in sorted(world.mandates.items())
            if m.association_id == association_id
        },
        "canon_authority": False,
    }
