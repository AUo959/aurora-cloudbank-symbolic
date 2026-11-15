"""P3 synthetic policy experiment: agent -> institution -> material consequence.

No historical Galactic Union event is asserted. Every polity/actor name is
fixture data, not canon, and all operations use the isolated L2 kernel.
"""
from __future__ import annotations

from .bindings import identity_binding_view
from .external_evidence import observe_ace_identity
from .kernel import CausalEngine
from .model import Actor, Institution
from .political_actions import institution_view, prepare_relief_proposal
from .scenario import fixture


def p3_fixture():
    world = fixture()
    world.actors["member_a"] = Actor("member_a", "union_depot")
    world.actors["member_b"] = Actor("member_b", "union_depot")
    world.institutions["relief_council"] = Institution(
        "relief_council", "union_depot",
        ("governor", "member_a", "member_b"),
        quorum=2, approval_threshold=2, polity_id="fixture_union")
    return world


def synthetic_ace_projection() -> dict:
    world = {
        "world_id": "synthetic-p3-ace-world",
        "world_scope": "isolated_aurora_world",
        "status": "ready",
        "canonical_workspace_authority": False,
        "canon_head": "a" * 40,
        "sources": {
            "root": {"commit": "b" * 40},
            "CanonRec": {"commit": "c" * 40},
            "aurora-cloudbank-symbolic-main": {"commit": "d" * 40},
        },
    }
    character = {
        "world_id": world["world_id"],
        "world_scope": "isolated_aurora_world",
        "request_id": "synthetic-p3-read",
        "operation": "retrieve", "status": "RETRIEVED_CANON",
        "determination_id": "synthetic-p3-determination",
        "entity_id": "fixture_governor_identity",
        "character": {
            "canonical_id": "fixture_governor_identity",
            "name": "Fixture Governor",
            "background": "Synthetic private detail excluded from committed identity.",
        },
        "origin": "sandbox_created",
    }
    return observe_ace_identity(world, character)


def run_p3(*, council_choice: str = "approve") -> dict:
    if council_choice not in ("approve", "reject"):
        raise ValueError("synthetic council_choice must be approve or reject")
    engine = CausalEngine(p3_fixture(), run_id=f"synthetic-p3-{council_choice}")
    ace = synthetic_ace_projection()
    state = engine.state
    grant = {
        "schema": "gumas.unified.fixture_binding_grant.p2",
        "operation": "bind_fixture_identity", "scope": "synthetic_fixture_only",
        "grant_ref": "fixture:p3-governor-binding",
        "operator_intent_explicit": True,
        "run_id": engine.run_id,
        "state_sha256": state.digest(),
        "actor_id": "governor", "site_id": "union_depot",
        "world_id": ace["world_id"], "entity_id": ace["entity_id"],
        "ace_projection_sha256": ace["projection_sha256"],
        "effective_at_s": state.time_s, "valid_until_s": 60,
        "allow_canon_promotion": False,
        "allow_agent_memory_injection": False,
        "allow_permission_changes": False,
    }
    engine.bind_fixture_identity(ace, grant)
    engine.disrupt_route("corridor_a", 4, cause="fixture:p3-corridor-disruption")

    proposal = prepare_relief_proposal(
        engine, institution_id="relief_council", proposer_id="governor",
        route_id="corridor_a", commodity="rations", amount=3, expires_s=30)
    motion = engine.propose_relief(proposal, cause="actor:governor-relief-motion")
    motion_id = motion.effect["motion_id"]
    engine.cast_relief_vote(
        motion_id, "governor", True, cause="actor:governor-yes")
    engine.cast_relief_vote(
        motion_id, "member_a", council_choice == "approve",
        cause="actor:member-a-ballot")

    after_ballots = institution_view(engine, "relief_council")
    after_reservation = None
    if council_choice == "approve":
        engine.ratify_relief(
            motion_id, "member_a", cause="institution:quorum-and-threshold")
        after_reservation = {
            "origin": engine.site_view("union_depot"),
            "union": engine.polity_view("fixture_union"),
            "institution": institution_view(engine, "relief_council"),
        }
        engine.dispatch_ratified_relief(
            motion_id, "governor", cause="actor:governor-executes-motion")
    else:
        engine.cast_relief_vote(
            motion_id, "member_b", False, cause="actor:member-b-ballot")

    engine.send_report(
        "governor", "observer", "corridor_a",
        f"Relief motion outcome: {council_choice}",
        cause="actor:governor-notifies-frontier")

    departure = {
        "origin": engine.site_view("union_depot"),
        "destination": engine.site_view("frontier_port"),
        "union": engine.polity_view("fixture_union"),
        "frontier": engine.polity_view("fixture_frontier"),
        "institution": institution_view(engine, "relief_council"),
        "remote_observer": engine.actor_view("observer"),
    }
    engine.advance_to(3)
    before_report = engine.actor_view("observer")
    engine.advance_to(4)
    after_report = engine.actor_view("observer")
    engine.advance_to(12)
    arrival = {
        "origin": engine.site_view("union_depot"),
        "destination": engine.site_view("frontier_port"),
        "union": engine.polity_view("fixture_union"),
        "frontier": engine.polity_view("fixture_frontier"),
        "institution": institution_view(engine, "relief_council"),
    }
    return {
        "scope": "synthetic_L2_only",
        "council_choice": council_choice,
        "binding": identity_binding_view(engine, "governor"),
        "ballots": after_ballots,
        "reservation": after_reservation,
        "departure": departure,
        "before_report": before_report,
        "after_report": after_report,
        "arrival": arrival,
        "evidence": engine.evidence(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps({
        "approve": run_p3(council_choice="approve"),
        "reject": run_p3(council_choice="reject"),
    }, sort_keys=True, indent=2))
