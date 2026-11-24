"""P4 governance protocols: data-driven decision rules, no polity-name branching.

Only synthetic local institutions are supported. This module evaluates a
recorded political decision; it does not perform physics, mint actors,
authenticate grants, write canon, or task L1/QGIA. The P3 quorum rule remains
the default when no P4 override is present.
"""
from __future__ import annotations

from .model import GovernanceProtocol, Institution, ReliefMotion, Universe

KINDS = frozenset(("delegated", "unanimous", "veto"))


def _validate_delegated(institution: Institution, rule: GovernanceProtocol,
                        members: set[str]) -> None:
    if (rule.delegate_id not in members or rule.veto_ids
            or institution.quorum != 1
            or institution.approval_threshold != 1):
        raise ValueError("delegation requires one member and one-vote ratification")


def _validate_unanimous(institution: Institution, rule: GovernanceProtocol,
                        members: set[str]) -> None:
    if (rule.delegate_id is not None or rule.veto_ids
            or institution.quorum != len(members)
            or institution.approval_threshold != len(members)):
        raise ValueError("unanimous consent must include every member")


def _validate_veto(rule: GovernanceProtocol, members: set[str]) -> None:
    if (rule.delegate_id is not None or not rule.veto_ids
            or len(rule.veto_ids) != len(set(rule.veto_ids))
            or not set(rule.veto_ids).issubset(members)):
        raise ValueError("veto holders must be distinct recorded members")


def validate_protocol(institution: Institution, rule: GovernanceProtocol) -> None:
    """Check static institutional constraints, not one civilization's norms."""
    if (rule.institution_id != institution.institution_id
            or not isinstance(rule.kind, str) or rule.kind not in KINDS
            or not isinstance(rule.veto_ids, tuple)):
        raise ValueError("unknown or mismatched synthetic governance protocol")
    members = set(institution.members)
    if rule.kind == "delegated":
        _validate_delegated(institution, rule, members)
    elif rule.kind == "unanimous":
        _validate_unanimous(institution, rule, members)
    elif rule.kind == "veto":
        _validate_veto(rule, members)


def rule_for(world: Universe, institution_id: str) -> GovernanceProtocol | None:
    """Missing P4 policy means the original P3 quorum/threshold behavior."""
    return world.governance_rules.get(institution_id)


def ballot_eligible(world: Universe, motion: ReliefMotion, actor_id: str) -> bool:
    institution = world.institutions[motion.institution_id]
    rule = rule_for(world, institution.institution_id)
    if actor_id not in institution.members:
        return False
    return rule is None or rule.kind != "delegated" or actor_id == rule.delegate_id


def _threshold_ready(institution: Institution, votes: dict[str, bool]) -> bool:
    return (
        len(votes) >= institution.quorum
        and sum(votes.values()) >= institution.approval_threshold
    )


def approval_ready(world: Universe, motion: ReliefMotion) -> bool:
    """Deterministically derive ratifiability from actual recorded ballots."""
    institution = world.institutions[motion.institution_id]
    rule = rule_for(world, institution.institution_id)
    votes = motion.votes
    if rule is None:
        return _threshold_ready(institution, votes)
    if rule.kind == "delegated":
        return votes.get(rule.delegate_id) is True
    if rule.kind == "unanimous":
        return len(votes) == len(institution.members) and all(votes.values())
    if rule.kind == "veto":
        return (
            _threshold_ready(institution, votes)
            and all(votes.get(vetoer) is True for vetoer in rule.veto_ids)
        )
    return False


def unreachable_approval(world: Universe, motion: ReliefMotion) -> bool:
    """Whether more *feasible* ballots could not make this motion pass."""
    institution = world.institutions[motion.institution_id]
    rule = rule_for(world, institution.institution_id)
    votes = motion.votes
    if rule is not None:
        if rule.kind == "delegated":
            return votes.get(rule.delegate_id) is False
        if rule.kind == "unanimous":
            return any(v is False for v in votes.values())
        if rule.kind == "veto" and any(
            votes.get(vetoer) is False for vetoer in rule.veto_ids
        ):
            return True
    # The default and veto protocols still have a general approval threshold.
    remaining = len(institution.members) - len(votes)
    return sum(votes.values()) + remaining < institution.approval_threshold


def protocol_label(world: Universe, institution_id: str) -> str:
    rule = rule_for(world, institution_id)
    return rule.kind if rule is not None else "quorum_threshold_p3"
