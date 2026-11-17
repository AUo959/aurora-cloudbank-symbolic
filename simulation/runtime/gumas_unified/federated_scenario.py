"""P6: a seatless association forms and makes a material choice with delays.

Synthetic member locations are in different site-polity labels. The association
is created by reciprocal explicit consent, not inherited from either polity.
No special-case civilization model, canonical identity, real-world authority,
or automatic physical dispatch is created.
"""
from __future__ import annotations

from .federated_actions import association_view
from .kernel import CausalEngine
from .political_scenario import p3_fixture
from .model import Corridor
from .governance_scenario import governance_fixture


def federated_fixture():
    world = governance_fixture("veto")
    world.actors["member_b"].site_id = "frontier_port"
    world.corridors["return_signal"] = Corridor(
        "return_signal", "frontier_port", "union_depot",
        distance_km=1200, cargo_speed_km_s=100,
        signal_speed_km_s=300, capacity_units_per_window=6,
        window_seconds=60, signal_energy_j_per_km=1,
        shipment_energy_j_per_unit_km=1,
    )
    return world


def _charter(engine: CausalEngine, *, accept: bool) -> tuple[str, str | None, dict]:
    offered = engine.offer_charter(
        "governor", "member_b", "Voluntary intersite relief association",
        "corridor_a", expires_s=42, cause="actor:founder-invites")
    cid = offered.effect["charter_id"]
    engine.advance_to(3)
    before_offer = engine.actor_view("member_b")
    engine.advance_to(4)
    after_offer = engine.actor_view("member_b")
    engine.respond_charter(
        cid, "member_b", accept, "return_signal",
        cause="actor:invitee-individual-consent")
    engine.advance_to(7)
    founder_before_consent = engine.actor_view("governor")
    engine.advance_to(8)
    founder_after_consent = engine.actor_view("governor")
    assoc = engine.state.charters[cid].association_id
    return cid, assoc, {
        "offer_before": before_offer,
        "offer_after": after_offer,
        "founder_before_response": founder_before_consent,
        "founder_after_response": founder_after_consent,
    }


def run_p6(*, charter_accept: bool = True,
           mandate_approve: bool = True) -> dict:
    engine = CausalEngine(
        federated_fixture(),
        run_id=f"synthetic-p6-{charter_accept}-{mandate_approve}")
    cid, aid, knowledge = _charter(engine, accept=charter_accept)
    if not charter_accept:
        engine.advance_to(28)
        return {
            "schema": "gumas.unified.seatless_association_scenario.p6",
            "authority": "synthetic_L2_only",
            "charter_id": cid,
            "association_formed": False,
            "knowledge": knowledge,
            "origin": engine.site_view("union_depot"),
            "destination": engine.site_view("frontier_port"),
            "evidence": engine.evidence(),
        }
    engine.confirm_association(
        aid, "governor", cause="actor:founder-acknowledges-formation")
    proposed = engine.propose_mandate(
        aid, "governor", "corridor_a", "corridor_a", "rations", 3,
        expires_s=44, cause="actor:founder-proposes-relief")
    mid = proposed.effect["mandate_id"]
    engine.advance_to(11)
    remote_before = engine.actor_view("member_b")
    engine.advance_to(12)
    remote_after = engine.actor_view("member_b")
    engine.respond_mandate(
        mid, "member_b", mandate_approve, "return_signal",
        cause="actor:remote-member-decides")
    engine.advance_to(15)
    founder_before = engine.actor_view("governor")
    engine.advance_to(16)
    founder_after = engine.actor_view("governor")
    before_execution = association_view(engine, aid)
    shipment = None
    if mandate_approve:
        shipment = engine.execute_mandate(
            mid, "governor", cause="actor:custodian-acts-after-consent")
    after_execution = association_view(engine, aid)
    engine.advance_to(28)
    return {
        "schema": "gumas.unified.seatless_association_scenario.p6",
        "authority": "synthetic_L2_only",
        "charter_id": cid,
        "association_id": aid,
        "association_formed": True,
        "knowledge": knowledge,
        "remote_before_mandate": remote_before,
        "remote_after_mandate": remote_after,
        "founder_before_vote": founder_before,
        "founder_after_vote": founder_after,
        "before_execution": before_execution,
        "after_execution": after_execution,
        "shipment": None if shipment is None else shipment.effect,
        "origin": engine.site_view("union_depot"),
        "destination": engine.site_view("frontier_port"),
        "association": association_view(engine, aid),
        "evidence": engine.evidence(),
    }


def run_remote_initiative() -> dict:
    """A confirmed member can coordinate from the other physical site."""
    engine = CausalEngine(federated_fixture(),
                          run_id="synthetic-p6-remote-initiative")
    _, aid, _ = _charter(engine, accept=True)
    engine.confirm_association(
        aid, "governor", cause="actor:founder-transmits-confirmation")
    engine.advance_to(12)
    proposed = engine.propose_mandate(
        aid, "member_b", "return_signal", "return_signal",
        "rations", 1, expires_s=40,
        cause="actor:remote-member-initiates-new-proposal")
    mid = proposed.effect["mandate_id"]
    engine.advance_to(16)
    engine.respond_mandate(
        mid, "governor", True, "corridor_a",
        cause="actor:founder-accepts-remote-initiative")
    engine.advance_to(20)
    execution = engine.execute_mandate(
        mid, "member_b", cause="actor:remote-custodian-physically-executes")
    engine.advance_to(32)
    return {
        "schema": "gumas.unified.remote_initiative_scenario.p6",
        "authority": "synthetic_L2_only",
        "association_id": aid,
        "mandate_id": mid,
        "execution": execution.effect,
        "origin": engine.site_view("frontier_port"),
        "destination": engine.site_view("union_depot"),
        "association": association_view(engine, aid),
        "evidence": engine.evidence(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps({
        "accepted_and_authorized": run_p6(),
        "charter_declined": run_p6(charter_accept=False),
        "mandate_rejected": run_p6(mandate_approve=False),
        "remote_initiative": run_remote_initiative(),
    }, sort_keys=True, indent=2))
