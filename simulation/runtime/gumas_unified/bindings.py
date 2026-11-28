"""P2 synthetic-only ACE identity binding contract.

One explicit fixture grant can bind a P1 ACE identity reference to an existing
P0 agent inside the isolated L2 kernel. The grant is NOT cryptographically
authenticated and does not assert source-canon authorization. The binding may
change identity labels, not actor capabilities, preferences, permissions or
observations. The kernel alone commits this record.
"""
from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any

from .external_evidence import (
    EvidenceError, canonical_sha256, digest_without, fields_match, is_synthetic_engine,
)
from .kernel import CausalEngine

_SHA40 = re.compile(r"[0-9a-f]{40}\Z")
_SHA64 = re.compile(r"[0-9a-f]{64}\Z")
_ACE_SCHEMA = "gumas.unified.ace_identity_reference.p1"
_BINDING_SCHEMA = "gumas.unified.fixture_identity_binding.p2"
_GRANT_FIELDS = frozenset({
    "schema", "operation", "scope", "grant_ref", "operator_intent_explicit",
    "run_id", "state_sha256", "actor_id", "site_id", "world_id", "entity_id",
    "ace_projection_sha256", "effective_at_s", "valid_until_s",
    "allow_canon_promotion", "allow_agent_memory_injection",
    "allow_permission_changes",
})
_ACE_CLAIMS = {
    "schema": _ACE_SCHEMA,
    "authority": "unverified_external_observation_only",
    "world_scope": "isolated_aurora_world",
    "identity_bound_to_l2_actor": False,
    "source_canon_promoted": False,
}
_ACE_SOURCE_REPOS = frozenset({"root", "CanonRec", "aurora-cloudbank-symbolic-main"})
_GRANT_SCOPE = {
    "schema": "gumas.unified.fixture_binding_grant.p2",
    "operation": "bind_fixture_identity",
    "scope": "synthetic_fixture_only",
    "operator_intent_explicit": True,
}
_GRANT_REFUSALS = {
    "allow_canon_promotion": False,
    "allow_agent_memory_injection": False,
    "allow_permission_changes": False,
}


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not 0 < len(value) <= 256 or not value.strip():
        raise EvidenceError(f"{label} must be a bounded nonempty string")
    return value


def _sha(value: Any, label: str, length: int) -> str:
    if not isinstance(value, str) or not (
        _SHA40 if length == 40 else _SHA64
    ).fullmatch(value):
        raise EvidenceError(f"{label} has invalid sha shape")
    return value


def _nat(value: Any, label: str) -> int:
    if type(value) is not int or not 0 <= value <= 10**15:
        raise EvidenceError(f"{label} must be a bounded nonnegative integer")
    return value


def _validate_source_pins(pins: Any) -> None:
    if not isinstance(pins, Mapping) or set(pins) != _ACE_SOURCE_REPOS:
        raise EvidenceError("ACE source pins missing")
    for name, sha in pins.items():
        _sha(sha, name, 40)


def _validate_ace_projection(ace: Mapping[str, Any]) -> None:
    if not isinstance(ace, Mapping):
        raise EvidenceError("ACE source projection is not an object")
    if not fields_match(ace, _ACE_CLAIMS):
        raise EvidenceError("ACE projection has unapproved identity authority")
    expected = _sha(ace.get("projection_sha256"), "ACE projection sha", 64)
    if digest_without(ace, "projection_sha256") != expected:
        raise EvidenceError("ACE projection checksum mismatch")
    _string(ace.get("world_id"), "world_id")
    _string(ace.get("entity_id"), "entity_id")
    _string(ace.get("name"), "ACE name")
    _string(ace.get("determination_id"), "determination_id")
    if ace.get("origin") not in {"sandbox_created", "inherited_canon"}:
        raise EvidenceError("ACE origin not established")
    _validate_source_pins(ace.get("source_pins"))
    _sha(ace.get("sandbox_canon_head"), "sandbox head", 40)


def _binding_grant_in_scope(grant: Mapping[str, Any]) -> bool:
    return (fields_match(grant, _GRANT_SCOPE)
            and isinstance(grant["grant_ref"], str)
            and grant["grant_ref"].startswith("fixture:")
            and fields_match(grant, _GRANT_REFUSALS))


def _binding_grant_anchored(engine: CausalEngine, state: Any, grant: Mapping[str, Any],
                            ace: Mapping[str, Any], actor: Any) -> bool:
    return (grant["run_id"] == engine.run_id and grant["site_id"] == actor.site_id
            and grant["state_sha256"] == state.digest()
            and fields_match(grant, {
                "world_id": ace["world_id"],
                "entity_id": ace["entity_id"],
                "ace_projection_sha256": ace["projection_sha256"],
            }))


def _binding_window(state: Any, grant: Mapping[str, Any]) -> tuple[int, int]:
    at = _nat(grant["effective_at_s"], "effective_at_s")
    until = _nat(grant["valid_until_s"], "valid_until_s")
    if at != state.time_s or until <= at:
        raise EvidenceError("binding window is stale or invalid")
    return at, until


def _require_unbound(state: Any, actor_id: str, ace: Mapping[str, Any]) -> None:
    if actor_id in state.identity_bindings:
        raise EvidenceError("actor already bound within this synthetic world")
    target = (ace["world_id"], ace["entity_id"])
    for existing in state.identity_bindings.values():
        if (existing["world_id"], existing["entity_id"]) == target:
            raise EvidenceError("same ACE identity already bound to a different actor")


def _identity_binding_record(engine: CausalEngine, ace: Mapping[str, Any],
                             grant: Mapping[str, Any], actor_id: str, actor: Any,
                             window: tuple[int, int]) -> dict[str, Any]:
    at, until = window
    record: dict[str, Any] = {
        "schema": _BINDING_SCHEMA,
        "scope": "synthetic_fixture_only",
        "actor_id": actor_id,
        "site_id_at_binding": actor.site_id,
        "run_id": engine.run_id,
        "world_id": ace["world_id"],
        "entity_id": ace["entity_id"],
        "name": ace["name"],
        "origin": ace["origin"],
        "ace_projection_sha256": ace["projection_sha256"],
        "grant_sha256": canonical_sha256(dict(grant)),
        "grant_ref": grant["grant_ref"],
        "bound_at_s": at,
        "valid_until_s": until,
        "grant_authenticated": False,
        "source_canon_promoted": False,
        "actor_permissions_changed": False,
        "agent_memory_injected": False,
    }
    record["binding_sha256"] = canonical_sha256(record)
    return record


def prepare_fixture_identity_binding(engine: CausalEngine,
                                     ace_projection: Mapping[str, Any],
                                     grant: Mapping[str, Any]) -> dict[str, Any]:
    """Validate an explicit, *untrusted fixture-only* operator intention.

    This creates a proposal value only. It neither commits it nor grants
    real-world authority. P2 never infers permission from names, titles or
    the fact that a source says "RETRIEVED_CANON".
    """
    if not is_synthetic_engine(engine):
        raise EvidenceError("P2 identity binding requires an isolated synthetic L2 run")
    _validate_ace_projection(ace_projection)
    if not isinstance(grant, Mapping) or set(grant) != _GRANT_FIELDS:
        raise EvidenceError("binding grant must have exact approved fixture fields")
    if not _binding_grant_in_scope(grant):
        raise EvidenceError("binding grant exceeds fixture-only authority")
    _string(grant["grant_ref"], "grant_ref")
    state = engine.state
    actor_id = _string(grant["actor_id"], "actor_id")
    actor = state.actors.get(actor_id)
    if actor is None:
        raise EvidenceError("target L2 actor is absent")
    if not _binding_grant_anchored(engine, state, grant, ace_projection, actor):
        raise EvidenceError("binding grant is not anchored to this run and source")
    _sha(grant["state_sha256"], "grant state", 64)
    _sha(grant["ace_projection_sha256"], "grant source", 64)
    window = _binding_window(state, grant)
    _require_unbound(state, actor_id, ace_projection)
    return _identity_binding_record(engine, ace_projection, grant, actor_id, actor, window)


def identity_binding_view(engine: CausalEngine, actor_id: str) -> dict[str, Any]:
    """Review a kernel-committed binding without modifying simulated knowledge."""
    if not isinstance(engine, CausalEngine):
        raise EvidenceError("identity view requires an L2 engine")
    state = engine.state
    record = state.identity_bindings.get(actor_id)
    if record is None:
        raise EvidenceError("actor has no synthetic L2 identity binding")
    if canonical_sha256({k: v for k, v in record.items()
                         if k != "binding_sha256"}) != record["binding_sha256"]:
        raise EvidenceError("committed identity binding checksum mismatch")
    return {
        "schema": "gumas.unified.identity_binding_view.p2",
        "authority": "synthetic_L2_identity_only",
        "run_id": engine.run_id,
        "actor_id": actor_id,
        "world_id": record["world_id"],
        "entity_id": record["entity_id"],
        "source_ref_sha256": record["ace_projection_sha256"],
        "binding_sha256": record["binding_sha256"],
        "effective_at_s": record["bound_at_s"],
        "valid_until_s": record["valid_until_s"],
        "active_at_current_time": record["bound_at_s"] <= state.time_s < record["valid_until_s"],
        "source_canon_promoted": False,
        "permissions_changed": False,
        "agent_memory_injected": False,
        "external_identity_authenticated": False,
    }
