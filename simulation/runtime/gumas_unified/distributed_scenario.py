"""P5 geographically distributed governance under one synthetic causal field.

A remote member belongs to institutions on both sides of a polity boundary.
They receive the motion notice only after a directed light-delay, and their
ballot becomes institutionally countable only after the return signal.
These invented fixtures have no canonical political identity.
"""
from __future__ import annotations

from .distributed_actions import distributed_council_view
from .governance_scenario import governance_fixture
from .kernel import CausalEngine
from .model import Corridor, GovernanceProtocol, Institution
from .political_actions import institution_view, prepare_relief_proposal


def distributed_fixture(protocol: str):
    world = governance_fixture(protocol)
    world.actors["member_b"].site_id = "frontier_port"
    world.corridors["return_signal"] = Corridor(
        "return_signal", "frontier_port", "union_depot",
        distance_km=1200, cargo_speed_km_s=100,
        signal_speed_km_s=300, capacity_units_per_window=6,
        window_seconds=60, signal_energy_j_per_km=1,
        shipment_energy_j_per_unit_km=1,
    )
    # A participant can have overlapping non-exclusive organizational roles.
    # Membership says nothing about territorial sovereignty or canon status.
    world.institutions["frontier_assembly"] = Institution(
        "frontier_assembly", "frontier_port", ("member_b", "observer"),
        quorum=2, approval_threshold=2, polity_id="fixture_frontier",
    )
    if protocol == "delegated":
        world.governance_rules["relief_council"] = GovernanceProtocol(
            "relief_council", "delegated", delegate_id="member_b")
    return world


def _propose(engine: CausalEngine, *, expires_s: int) -> str:
    prepared = prepare_relief_proposal(
        engine, institution_id="relief_council", proposer_id="governor",
        route_id="corridor_a", commodity="rations", amount=3,
        expires_s=expires_s)
    return engine.propose_relief(
        prepared, cause="actor:local-proposal").effect["motion_id"]


def run_distributed(protocol: str = "veto", *, remote_approves: bool = True) -> dict:
    if protocol not in ("delegated", "unanimous", "veto"):
        raise ValueError("unsupported synthetic P5 governance protocol")
    engine = CausalEngine(
        distributed_fixture(protocol),
        run_id=f"synthetic-p5-{protocol}-{remote_approves}",
    )
    engine.disrupt_route("corridor_a", 4, cause="fixture:p5-cargo-capacity")
    motion_id = _propose(engine, expires_s=28)
    if protocol != "delegated":
        engine.cast_relief_vote(
            motion_id, "governor", True, cause="actor:governor-consent")
        engine.cast_relief_vote(
            motion_id, "member_a", True, cause="actor:member-a-consent")

    engine.send_policy_notice(
        motion_id, "governor", "member_b", "corridor_a",
        cause="actor:notify-distant-member",
    )
    engine.advance_to(3)
    before_notice = engine.actor_view("member_b")
    before_notice_council = institution_view(engine, "relief_council")
    engine.advance_to(4)
    after_notice = engine.actor_view("member_b")
    remote_sent = engine.submit_remote_ballot(
        motion_id, "member_b", remote_approves, "return_signal",
        cause="actor:remote-deliberated-choice",
    )
    engine.advance_to(7)
    before_ballot = distributed_council_view(engine, "relief_council")
    engine.advance_to(8)
    counted_council = distributed_council_view(engine, "relief_council")
    if remote_approves:
        engine.ratify_relief(
            motion_id, "governor", cause="institution:received-required-consent")
        engine.dispatch_ratified_relief(
            motion_id, "governor", cause="actor:deliver-approved-physical-aid")
    engine.send_report(
        "governor", "observer", "corridor_a",
        f"Relief motion {motion_id}: {'approved' if remote_approves else 'rejected'}",
        cause="actor:notify-remote-observer",
    )
    engine.advance_to(11)
    observer_before_report = engine.actor_view("observer")
    engine.advance_to(12)
    observer_after_report = engine.actor_view("observer")
    engine.advance_to(20)
    return {
        "schema": "gumas.unified.distributed_governance_scenario.p5",
        "authority": "synthetic_L2_only",
        "protocol": protocol,
        "remote_approves": remote_approves,
        "motion_id": motion_id,
        "seat_member_polities": {
            "relief_council": "fixture_union",
            "remote_member_location": "fixture_frontier",
            "overlapping_membership": ["relief_council", "frontier_assembly"],
        },
        "before_notice": before_notice,
        "before_notice_council": before_notice_council,
        "after_notice": after_notice,
        "remote_ballot_sent": remote_sent.effect,
        "before_ballot": before_ballot,
        "counted_council": counted_council,
        "observer_before_report": observer_before_report,
        "observer_after_report": observer_after_report,
        "at_20s": {
            "origin": engine.site_view("union_depot"),
            "destination": engine.site_view("frontier_port"),
            "institution": institution_view(engine, "relief_council"),
        },
        "evidence": engine.evidence(),
    }


def run_late_ballot() -> dict:
    """Ballot sent while a motion is open, received after it has expired."""
    engine = CausalEngine(distributed_fixture("veto"),
                          run_id="synthetic-p5-late-ballot")
    motion_id = _propose(engine, expires_s=6)
    engine.cast_relief_vote(
        motion_id, "governor", True, cause="actor:governor-consent")
    engine.cast_relief_vote(
        motion_id, "member_a", True, cause="actor:member-a-consent")
    engine.send_policy_notice(
        motion_id, "governor", "member_b", "corridor_a",
        cause="actor:notice-before-deadline")
    engine.advance_to(4)
    sent = engine.submit_remote_ballot(
        motion_id, "member_b", True, "return_signal",
        cause="actor:ballot-sent-before-deadline")
    engine.advance_to(6)
    at_expiry = institution_view(engine, "relief_council")
    engine.advance_to(8)
    after_arrival = institution_view(engine, "relief_council")
    return {
        "schema": "gumas.unified.late_ballot_scenario.p5",
        "authority": "synthetic_L2_only",
        "sent": sent.effect,
        "at_expiry": at_expiry,
        "after_arrival": after_arrival,
        "final_ballot_status": next(iter(engine.state.remote_ballots.values())).status,
        "evidence": engine.evidence(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps({
        "distributed_veto_yes": run_distributed("veto"),
        "distributed_veto_no": run_distributed("veto", remote_approves=False),
        "distributed_unanimous": run_distributed("unanimous"),
        "distributed_delegated": run_distributed("delegated"),
        "late_ballot": run_late_ballot(),
    }, indent=2, sort_keys=True))
