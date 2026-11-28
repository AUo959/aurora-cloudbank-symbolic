"""P2 exact, synthetic-only coordinate mapping for Phase-9 relative time.

This projects tactical elapsed milliseconds to the P0 L2 millisecond
coordinate *without rounding* or advancing the P0 world. A user-declared
epoch correspondence is not synchronization evidence, source authenticity,
causal validity, or authority to execute any tactical step.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .external_evidence import EvidenceError, canonical_sha256
from .kernel import CausalEngine

_PHASE9_SCHEMA = "gumas.unified.phase9_ledger_reference.p1"
_CLOCK_GRANT_FIELDS = frozenset({
    "schema", "operation", "scope", "grant_ref", "operator_intent_explicit",
    "run_id", "local_state_sha256", "local_epoch_s",
    "external_projection_sha256", "external_run_identity_sha256",
    "external_ledger_tail_sha256", "reference_frame_id",
    "rate", "allow_execution", "allow_canon_time_promotion",
})


def _bounded(value: Any, label: str) -> str:
    if not isinstance(value, str) or not 0 < len(value) <= 256 or not value.strip():
        raise EvidenceError(f"{label} must be a bounded string")
    return value


def _nonnegative(value: Any, label: str) -> int:
    if type(value) is not int or not 0 <= value <= 10**15:
        raise EvidenceError(f"{label} must be a bounded nonnegative integer")
    return value


def _verified_projection(projection: Mapping[str, Any]) -> None:
    if not isinstance(projection, Mapping):
        raise EvidenceError("tactical projection is not an object")
    allowed = {
        "schema", "authority", "source_contract",
        "phase9_entries_structurally_verified", "execution_authorized",
        "run0_executed", "run_identity_sha256", "t0_roster_sha256",
        "last_ledger_entry_sha256", "elapsed_ms_at_tail", "time_basis",
        "clock_aligned_to_unified", "last_recorded_termination_mode",
        "full_state_replay_verified", "projection_sha256",
    }
    if set(projection) != allowed:
        raise EvidenceError("unexpected tactical projection fields")
    if (projection.get("source_contract")
            != "GUMAS_LIVE_OBSERVATION_ORCHESTRATOR_LEDGER_v1_0"
            or type(projection.get("phase9_entries_structurally_verified")) is not int
            or not 1 <= projection["phase9_entries_structurally_verified"] <= 128
            or not isinstance(projection.get("last_recorded_termination_mode"), str)
            or not projection["last_recorded_termination_mode"]):
        raise EvidenceError("tactical projection lacks a valid accepted Phase-9 span")
    if (projection.get("schema") != _PHASE9_SCHEMA
            or projection.get("authority") != "unverified_external_observation_only"
            or projection.get("time_basis") != "relative_to_external_tactical_T0"
            or projection.get("clock_aligned_to_unified") is not False
            or projection.get("execution_authorized") is not False
            or projection.get("run0_executed") is not False
            or projection.get("full_state_replay_verified") is not False):
        raise EvidenceError("tactical evidence makes unapproved time or execution claim")
    for key in ("run_identity_sha256", "t0_roster_sha256",
                "last_ledger_entry_sha256", "projection_sha256"):
        value = projection.get(key)
        if (not isinstance(value, str) or len(value) != 64
                or any(ch not in "0123456789abcdef" for ch in value)):
            raise EvidenceError("invalid tactical SHA256 field")
    if canonical_sha256({k: v for k, v in projection.items()
                         if k != "projection_sha256"}) != projection["projection_sha256"]:
        raise EvidenceError("tactical projection checksum mismatch")
    _nonnegative(projection.get("elapsed_ms_at_tail"), "tactical tail milliseconds")


def prepare_fixture_clock_anchor(engine: CausalEngine,
                                 tactical_projection: Mapping[str, Any],
                                 grant: Mapping[str, Any]) -> dict[str, Any]:
    """Create an immutable-value P2 anchor for a *declarative* clock mapping.

    The anchor belongs to an exact local snapshot; it becomes stale on any
    state transition. Its P0 epoch is local sim seconds converted to ms.
    """
    if not isinstance(engine, CausalEngine) or not engine.run_id.startswith("synthetic-"):
        raise EvidenceError("clock anchor requires an isolated synthetic L2 run")
    _verified_projection(tactical_projection)
    if not isinstance(grant, Mapping) or set(grant) != _CLOCK_GRANT_FIELDS:
        raise EvidenceError("clock grant must have the exact allowed fields")
    if (grant["schema"] != "gumas.unified.clock_grant.p2"
            or grant["operation"] != "map_external_elapsed_ms"
            or grant["scope"] != "synthetic_fixture_only"
            or grant["operator_intent_explicit"] is not True
            or grant["allow_execution"] is not False
            or grant["allow_canon_time_promotion"] is not False
            or grant["rate"] != "1_ms_per_ms"
            or type(grant["rate"]) is not str
            or not isinstance(grant["grant_ref"], str)
            or not grant["grant_ref"].startswith("fixture:")):
        raise EvidenceError("clock grant exceeds synthetic reference-frame authority")
    _bounded(grant["grant_ref"], "clock grant_ref")
    if not _bounded(grant["reference_frame_id"], "frame id").startswith("fixture:"):
        raise EvidenceError("reference frame must be explicitly synthetic")
    local = engine.state
    epoch = _nonnegative(grant["local_epoch_s"], "local_epoch_s")
    if (grant["run_id"] != engine.run_id
            or grant["local_state_sha256"] != local.digest()
            or epoch != local.time_s
            or grant["external_projection_sha256"]
            != tactical_projection["projection_sha256"]
            or grant["external_run_identity_sha256"]
            != tactical_projection["run_identity_sha256"]
            or grant["external_ledger_tail_sha256"]
            != tactical_projection["last_ledger_entry_sha256"]):
        raise EvidenceError("clock anchor is not bound to the current snapshot/evidence")
    output = {
        "schema": "gumas.unified.fixture_clock_anchor.p2",
        "authority": "declared_synthetic_coordinate_mapping_only",
        "run_id": engine.run_id,
        "local_state_sha256": local.digest(),
        "reference_frame_id": grant["reference_frame_id"],
        "external_run_identity_sha256": tactical_projection["run_identity_sha256"],
        "external_projection_sha256": tactical_projection["projection_sha256"],
        "external_ledger_tail_sha256": tactical_projection["last_ledger_entry_sha256"],
        "external_tail_elapsed_ms": tactical_projection["elapsed_ms_at_tail"],
        "tactical_T0_at_local_ms": epoch * 1000,
        "rate": "1_ms_per_ms",
        "grant_sha256": canonical_sha256(dict(grant)),
        "external_source_authenticated": False,
        "clock_coordinate_mapping_declared": True,
        "physical_causality_verified": False,
        "can_advance_kernel_clock": False,
        "run0_executed": False,
        "canon_timeline_promoted": False,
    }
    output["anchor_sha256"] = canonical_sha256(output)
    return output


def project_tactical_interval(engine: CausalEngine,
                              tactical_projection: Mapping[str, Any],
                              anchor: Mapping[str, Any], *,
                              start_elapsed_ms: int, end_elapsed_ms: int) -> dict[str, Any]:
    """Map a bounded interval exactly, retaining subsecond precision.

    No write, resampling, physical event delivery or retiming of P0 events.
    """
    if not isinstance(engine, CausalEngine):
        raise EvidenceError("clock mapping requires a synthetic L2 engine")
    _verified_projection(tactical_projection)
    if not isinstance(anchor, Mapping):
        raise EvidenceError("clock anchor is not an object")
    if (anchor.get("schema") != "gumas.unified.fixture_clock_anchor.p2"
            or anchor.get("authority") != "declared_synthetic_coordinate_mapping_only"
            or anchor.get("external_source_authenticated") is not False
            or anchor.get("clock_coordinate_mapping_declared") is not True
            or anchor.get("physical_causality_verified") is not False
            or anchor.get("can_advance_kernel_clock") is not False
            or anchor.get("run0_executed") is not False
            or anchor.get("canon_timeline_promoted") is not False
            or anchor.get("rate") != "1_ms_per_ms"):
        raise EvidenceError("clock anchor contains unapproved authority")
    if (not isinstance(anchor.get("reference_frame_id"), str)
            or not anchor["reference_frame_id"].startswith("fixture:")
            or not isinstance(anchor.get("grant_sha256"), str)
            or len(anchor["grant_sha256"]) != 64
            or any(ch not in "0123456789abcdef"
                   for ch in anchor["grant_sha256"])):
        raise EvidenceError("invalid synthetic clock frame or grant reference")
    checksum = anchor.get("anchor_sha256")
    if checksum != canonical_sha256({k: v for k, v in anchor.items()
                                     if k != "anchor_sha256"}):
        raise EvidenceError("clock anchor digest mismatch")
    snapshot = engine.state
    if (anchor.get("run_id") != engine.run_id
            or anchor.get("local_state_sha256") != snapshot.digest()
            or anchor.get("external_projection_sha256")
            != tactical_projection["projection_sha256"]
            or anchor.get("external_run_identity_sha256")
            != tactical_projection["run_identity_sha256"]
            or anchor.get("external_ledger_tail_sha256")
            != tactical_projection["last_ledger_entry_sha256"]
            or anchor.get("external_tail_elapsed_ms")
            != tactical_projection["elapsed_ms_at_tail"]):
        raise EvidenceError("clock anchor is stale or bound to another source")
    start = _nonnegative(start_elapsed_ms, "start_elapsed_ms")
    end = _nonnegative(end_elapsed_ms, "end_elapsed_ms")
    tail = _nonnegative(anchor.get("external_tail_elapsed_ms"), "tail milliseconds")
    if not start < end <= tail:
        raise EvidenceError("mapped interval must fit the observed tactical ledger")
    epoch = _nonnegative(anchor.get("tactical_T0_at_local_ms"), "T0 local milliseconds")
    if epoch != snapshot.time_s * 1000:
        raise EvidenceError("clock anchor is not at this L2 snapshot's coordinate")
    mapped_start, mapped_end = epoch + start, epoch + end
    output = {
        "schema": "gumas.unified.fixture_tactical_interval.p2",
        "authority": "read_only_declared_coordinate_mapping",
        "run_id": engine.run_id,
        "local_state_sha256": snapshot.digest(),
        "anchor_sha256": checksum,
        "source_ledger_tail_sha256": anchor["external_ledger_tail_sha256"],
        "reference_frame_id": anchor["reference_frame_id"],
        "start_elapsed_ms": start,
        "end_elapsed_ms": end,
        "mapped_start_l2_ms": mapped_start,
        "mapped_end_l2_ms": mapped_end,
        "start_l2_second": mapped_start // 1000,
        "start_subsecond_ms": mapped_start % 1000,
        "end_l2_second": mapped_end // 1000,
        "end_subsecond_ms": mapped_end % 1000,
        "source_authenticated": False,
        "physical_causality_verified": False,
        "kernel_clock_advanced": False,
        "event_delivery_authorized": False,
        "canon_timeline_promoted": False,
    }
    output["projection_sha256"] = canonical_sha256(output)
    return output


def operator_cross_scale_frame(engine: CausalEngine, actor_id: str,
                               tactical_projection: Mapping[str, Any],
                               anchor: Mapping[str, Any], *,
                               start_elapsed_ms: int,
                               end_elapsed_ms: int) -> dict[str, Any]:
    """Reconcile an actual synthetic identity binding and declared clock map.

    This is a read-only operator view, not causal authorization, agent
    knowledge, or a merged canonical timeline.
    """
    from .bindings import identity_binding_view

    before, ledger = engine.state.digest(), engine.ledger
    identity = identity_binding_view(engine, actor_id)
    interval = project_tactical_interval(
        engine, tactical_projection, anchor,
        start_elapsed_ms=start_elapsed_ms, end_elapsed_ms=end_elapsed_ms)
    if not identity["active_at_current_time"]:
        raise EvidenceError("cannot use an expired synthetic identity binding")
    if engine.state.digest() != before or engine.ledger != ledger:
        raise AssertionError("cross-scale view changed L2 state or event history")
    return {
        "schema": "gumas.unified.cross_scale_operator_frame.p2",
        "authority": "synthetic_review_only_not_actor_knowledge",
        "run_id": engine.run_id,
        "local_state_sha256": before,
        "identity": identity,
        "tactical_interval": interval,
        "identity_binding_in_kernel": True,
        "tactical_execution_authorized": False,
        "tactical_effects_imported": False,
        "external_source_authenticated": False,
        "canon_mutation_permitted": False,
    }
