"""P4: three distinct synthetic organization forms, one physical reality.

Delegated authority, unanimous consent and veto-gated deliberation are
institutional *mechanisms*, not assertions about canonical civilizations.
No source-specific political rules or real-world actors are imported.
"""
from __future__ import annotations

from .kernel import CausalEngine
from .model import GovernanceProtocol, Institution
from .political_actions import prepare_relief_proposal, institution_view
from .political_scenario import p3_fixture


def governance_fixture(protocol: str):
    world = p3_fixture()
    members = ("governor", "member_a", "member_b")
    if protocol == "delegated":
        world.institutions["relief_council"] = Institution(
            "relief_council", "union_depot", members,
            quorum=1, approval_threshold=1, polity_id="fixture_union")
        rule = GovernanceProtocol("relief_council", "delegated", delegate_id="governor")
    elif protocol == "unanimous":
        world.institutions["relief_council"] = Institution(
            "relief_council", "union_depot", members,
            quorum=3, approval_threshold=3, polity_id="fixture_union")
        rule = GovernanceProtocol("relief_council", "unanimous")
    elif protocol == "veto":
        world.institutions["relief_council"] = Institution(
            "relief_council", "union_depot", members,
            quorum=2, approval_threshold=2, polity_id="fixture_union")
        rule = GovernanceProtocol(
            "relief_council", "veto", veto_ids=("member_b",))
    else:
        raise ValueError("not a synthetic P4 governance protocol")
    world.governance_rules["relief_council"] = rule
    return world


def run_p4(protocol: str = "delegated", *, veto_yes: bool = True) -> dict:
    """Take the same relief policy through one local institutional contract."""
    if protocol != "veto" and veto_yes is not True:
        raise ValueError("veto_yes only applies to the veto fixture")
    engine = CausalEngine(governance_fixture(protocol),
                          run_id=f"synthetic-p4-{protocol}-{veto_yes}")
    engine.disrupt_route("corridor_a", 4, cause="fixture:transport-disruption")
    proposal = prepare_relief_proposal(
        engine, institution_id="relief_council", proposer_id="governor",
        route_id="corridor_a", commodity="rations", amount=3, expires_s=30)
    motion_id = engine.propose_relief(proposal, cause="actor:relief-intent").effect["motion_id"]
    engine.cast_relief_vote(motion_id, "governor", True, cause="actor:governor-yes")

    if protocol in ("unanimous", "veto"):
        engine.cast_relief_vote(motion_id, "member_a", True,
                                cause="actor:member-a-yes")
    if protocol == "unanimous" or protocol == "veto":
        engine.cast_relief_vote(
            motion_id, "member_b", True if protocol == "unanimous" else veto_yes,
            cause="actor:member-b-decision")
    before_ratification = institution_view(engine, "relief_council")
    if protocol != "veto" or veto_yes:
        engine.ratify_relief(motion_id, "governor", cause="institution:rule-satisfied")
        engine.dispatch_ratified_relief(
            motion_id, "governor", cause="actor:physical-fulfillment")
    engine.send_report(
        "governor", "observer", "corridor_a",
        f"Governance outcome: {protocol} / {'approved' if protocol != 'veto' or veto_yes else 'rejected'}",
        cause="actor:report-outcome")
    before_report = engine.actor_view("observer")
    engine.advance_to(4)
    after_report = engine.actor_view("observer")
    engine.advance_to(12)
    return {
        "status": "L2_synthetic_noncanonical",
        "protocol": protocol,
        "before_ratification": before_ratification,
        "after": institution_view(engine, "relief_council"),
        "local": engine.site_view("union_depot"),
        "destination": engine.site_view("frontier_port"),
        "source_polity": engine.polity_view("fixture_union"),
        "recipient_polity": engine.polity_view("fixture_frontier"),
        "observer_before_signal": before_report,
        "observer_after_signal": after_report,
        "evidence": engine.evidence(),
    }


if __name__ == "__main__":
    import json
    result = {
        "delegated": run_p4("delegated"),
        "unanimous": run_p4("unanimous"),
        "veto_yes": run_p4("veto"),
        "veto_no": run_p4("veto", veto_yes=False),
    }
    print(json.dumps(result, sort_keys=True, indent=2))
