"""Read-only evidence projections from unmerged ACE and tactical contracts.

P1 does NOT import ACE, tactical runtime, CanonRec, or external file readers.
Callers supply snapshots from an independently authorized source. Hash checks
prove *internal consistency only*, not source authenticity or execution.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import hashlib
import json
import re
from typing import Any

from .kernel import CausalEngine

_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_ACE_SOURCES = ("root", "CanonRec", "aurora-cloudbank-symbolic-main")
_PHASE9_SCHEMA = "aurora://simulation/gumas/phase9_ledger_entry/v1.0"
_PHASE9_CONTRACT = "GUMAS_LIVE_OBSERVATION_ORCHESTRATOR_LEDGER_v1_0"
_PHASE9_HASH_FIELDS = (
    "run_identity_sha256", "t0_roster_sha256",
    "previous_committed_state_sha256", "phase5_state_sha256",
    "phase5_receipt_sha256", "phase6_state_sha256", "phase6_receipt_sha256",
    "phase7_state_sha256", "phase7_receipt_sha256",
    "phase8_next_state_sha256", "phase8_resolution_state_sha256",
    "phase8_receipt_sha256",
)


class EvidenceError(ValueError):
    """External evidence is missing a required invariant or authority boundary."""


def canonical_sha256(payload: Any) -> str:
    """Phase-9 canonical JSON profile (hash consistency, not authentication)."""
    try:
        data = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                          allow_nan=False, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError, OverflowError) as exc:
        raise EvidenceError("evidence is not canonical JSON") from exc
    return hashlib.sha256(data).hexdigest()


def _object(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or not all(isinstance(k, str) for k in value):
        raise EvidenceError(f"{name} must be a string-keyed object")
    return value


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise EvidenceError(f"{name} must be a nonempty bounded string")
    return value


def _sha(value: Any, name: str, *, length: int = 64) -> str:
    if not isinstance(value, str) or not (
        _HEX40 if length == 40 else _HEX64
    ).fullmatch(value):
        raise EvidenceError(f"{name} must be lowercase hex sha{length * 4 // 10}")
    return value


def _integer(value: Any, name: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise EvidenceError(f"{name} must be integer >= {minimum}")
    return value


def _hash_map(value: Any, name: str) -> dict[str, str]:
    mapping = _object(value, name)
    if not mapping or len(mapping) > 512:
        raise EvidenceError(f"{name} must be a nonempty bounded hash map")
    return {k: _sha(v, f"{name}.{k}") for k, v in sorted(mapping.items())
            if _string(k, f"{name} key")}


def observe_ace_identity(world_status: Mapping[str, Any],
                         character_response: Mapping[str, Any]) -> dict[str, Any]:
    """Project exactly one retrieved ACE sandbox identity, never create or promote.

    Source: root PR #85's World.verify() and World._result() response contracts.
    Returns a minimal non-authoritative identity reference; background,
    local filesystem paths, raw materializations, and private packets are omitted.
    """
    world = _object(world_status, "ACE world_status")
    response = _object(character_response, "ACE character_response")
    world_id = _string(world.get("world_id"), "world_id")
    if (world.get("status") != "ready"
            or world.get("world_scope") != "isolated_aurora_world"
            or world.get("canonical_workspace_authority") is not False):
        raise EvidenceError("ACE world must be a verified isolated read-only source")
    if (response.get("world_id") != world_id
            or response.get("world_scope") != "isolated_aurora_world"
            or response.get("operation") != "retrieve"
            or response.get("status") != "RETRIEVED_CANON"):
        raise EvidenceError("ACE response must be a successful same-world retrieval")
    if response.get("origin") not in ("sandbox_created", "inherited_canon"):
        raise EvidenceError("ACE identity origin is not established")
    subject = _object(response.get("character"), "ACE character")
    entity_id = _string(response.get("entity_id"), "entity_id")
    if subject.get("canonical_id") != entity_id:
        raise EvidenceError("ACE character identity mismatch")
    name = _string(subject.get("name"), "character name")
    determination_id = _string(response.get("determination_id"),
                                "determination_id")
    _string(response.get("request_id"), "request_id")
    sources = _object(world.get("sources"), "ACE world sources")
    if not all(src in sources for src in _ACE_SOURCES):
        raise EvidenceError("ACE world lacks required source repository pins")
    source_pins = {
        src: _sha(_object(sources[src], src).get("commit"),
                  f"ACE source {src}", length=40)
        for src in _ACE_SOURCES
    }
    canon_head = _sha(world.get("canon_head"), "sandbox canon head", length=40)
    result = {
        "schema": "gumas.unified.ace_identity_reference.p1",
        "authority": "unverified_external_observation_only",
        "world_scope": "isolated_aurora_world",
        "world_id": world_id,
        "entity_id": entity_id,
        "name": name,
        "origin": response["origin"],
        "determination_id": determination_id,
        "source_pins": source_pins,
        "sandbox_canon_head": canon_head,
        "source_canon_promoted": False,
        "identity_bound_to_l2_actor": False,
    }
    result["projection_sha256"] = canonical_sha256(result)
    return result


def _validated_phase9_entry(raw: Any) -> Mapping[str, Any]:
    entry = _object(raw, "Phase-9 ledger entry")
    if (entry.get("schema") != _PHASE9_SCHEMA
            or entry.get("phase9_contract_id") != _PHASE9_CONTRACT
            or entry.get("phase9_version") != "1.0.0"
            or entry.get("canonical_json_profile") != "aurora-canonical-json-v1"
            or entry.get("historical_canon_status") != "non_canon_simulation_instance"):
        raise EvidenceError("Phase-9 schema, provenance or authority mismatch")
    if entry.get("reporter_invoked") is not False or entry.get("run0_executed") is not False:
        raise EvidenceError("Phase-9 unapproved execution or reporter evidence")
    if not _object(entry.get("phase9_source_identity"), "Phase-9 source identity"):
        raise EvidenceError("missing Phase-9 source identity")
    if not _object(entry.get("accepted_source_identities"), "accepted source identities"):
        raise EvidenceError("missing accepted source identities")
    for field in _PHASE9_HASH_FIELDS:
        _sha(entry.get(field), field)
    _integer(entry.get("macrostep_index"), "macrostep_index", minimum=1)
    start = _integer(entry.get("start_elapsed_ms"), "start_elapsed_ms")
    end = _integer(entry.get("end_elapsed_ms"), "end_elapsed_ms")
    if end <= start:
        raise EvidenceError("Phase-9 time must advance")
    observations = _hash_map(entry.get("live_observation_sha256_by_side"),
                             "observation hashes")
    receipts = _hash_map(entry.get("live_observation_receipt_sha256_by_side"),
                         "observation receipt hashes")
    if set(observations) != set(receipts):
        raise EvidenceError("Phase-9 observation side identities mismatch")
    _hash_map(entry.get("phase4_decision_sha256_by_fleet"), "decision hashes")
    outcome = _object(entry.get("terminal_outcome"), "terminal outcome")
    _string(outcome.get("termination_mode"), "terminal outcome mode")
    _sha(entry.get("ledger_entry_sha256"), "ledger entry digest")
    hashed = {k: v for k, v in entry.items() if k != "ledger_entry_sha256"}
    if entry["ledger_entry_sha256"] != canonical_sha256(hashed):
        raise EvidenceError("Phase-9 ledger entry digest mismatch")
    return entry


def observe_phase9_ledger(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Project an independently supplied Phase-9 ledger without executing a step.

    Validates complete genesis-to-tail linkage. No battle results, resources,
    threat analysis, canonical identity, or authoritative state are imported.
    """
    if isinstance(entries, (str, bytes)) or not isinstance(entries, Sequence):
        raise EvidenceError("Phase-9 entries must be an ordered sequence")
    if not 1 <= len(entries) <= 128:
        raise EvidenceError("Phase-9 evidence needs 1..128 ledger entries")
    validated = [_validated_phase9_entry(e) for e in entries]
    first = validated[0]
    if (first["macrostep_index"] != 1
            or first["start_elapsed_ms"] != 0
            or first.get("previous_ledger_entry_sha256") != "GENESIS"):
        raise EvidenceError("Phase-9 ledger requires a genesis-bound first entry")
    prev = first
    for index, entry in enumerate(validated[1:], 2):
        if (entry["macrostep_index"] != index
                or entry.get("previous_ledger_entry_sha256") != prev["ledger_entry_sha256"]
                or entry["previous_committed_state_sha256"]
                != prev["phase8_next_state_sha256"]
                or entry["start_elapsed_ms"] != prev["end_elapsed_ms"]):
            raise EvidenceError("Phase-9 ledger linkage or time continuity failed")
        if (entry["run_identity_sha256"] != first["run_identity_sha256"]
                or entry["t0_roster_sha256"] != first["t0_roster_sha256"]):
            raise EvidenceError("Phase-9 run or roster identity drift")
        if prev["terminal_outcome"]["termination_mode"] != "ongoing":
            raise EvidenceError("Phase-9 entry follows a terminal outcome")
        prev = entry
    last = validated[-1]
    output = {
        "schema": "gumas.unified.phase9_ledger_reference.p1",
        "authority": "unverified_external_observation_only",
        "source_contract": _PHASE9_CONTRACT,
        "phase9_entries_structurally_verified": len(validated),
        "execution_authorized": False,
        "run0_executed": False,
        "run_identity_sha256": first["run_identity_sha256"],
        "t0_roster_sha256": first["t0_roster_sha256"],
        "last_ledger_entry_sha256": last["ledger_entry_sha256"],
        "elapsed_ms_at_tail": last["end_elapsed_ms"],
        "time_basis": "relative_to_external_tactical_T0",
        "clock_aligned_to_unified": False,
        "last_recorded_termination_mode": last["terminal_outcome"]["termination_mode"],
        "full_state_replay_verified": False,
    }
    output["projection_sha256"] = canonical_sha256(output)
    return output


def observe_phase9_acceptance(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Summarize a Phase-9 acceptance *claim*, not an executable ledger.

    The public acceptance receipt is evidence of a reported test, but contains
    no complete mutable battle checkpoint. Do not conflate it with Run 0.
    """
    src = _object(receipt, "Phase-9 acceptance receipt")
    contract = _object(src.get("contract"), "Phase-9 acceptance contract")
    witness = _object(src.get("accepted_one_step_witness"),
                      "Phase-9 acceptance witness")
    if (src.get("phase") != 9 or src.get("status") != "PASS"
            or src.get("historical_canon_status") != "non_canon_simulation_instance"
            or contract.get("contract_id") != _PHASE9_CONTRACT
            or contract.get("version") != "1.0.0"
            or src.get("run0_executed") is not False
            or src.get("run0_remains_blocked") is not True
            or witness.get("run0_executed") is not False
            or witness.get("reporter_invoked") is not False
            or witness.get("macrosteps_executed") != 1):
        raise EvidenceError("Phase-9 acceptance claim not in permitted one-step scope")
    for field in ("ledger_entry_sha256", "run_identity_sha256",
                  "t0_roster_sha256", "source_t0_sha256"):
        _sha(witness.get(field), f"acceptance witness {field}")
    _string(src.get("receipt_id"), "acceptance receipt id")
    output = {
        "schema": "gumas.unified.phase9_acceptance_reference.p1",
        "authority": "external_acceptance_claim_only",
        "receipt_id": src["receipt_id"],
        "recorded_status": "PASS",
        "accepted_one_step_ledger_sha256": witness["ledger_entry_sha256"],
        "run_identity_sha256": witness["run_identity_sha256"],
        "t0_roster_sha256": witness["t0_roster_sha256"],
        "source_t0_sha256": witness["source_t0_sha256"],
        "run0_executed": False,
        "run0_remains_blocked": True,
        "claim_cryptographically_authenticated": False,
        "full_state_replay_verified": False,
    }
    output["projection_sha256"] = canonical_sha256(output)
    return output


def operator_evidence_frame(engine: CausalEngine,
                            *projections: Mapping[str, Any]) -> dict[str, Any]:
    """Review-only combination. Never inject external evidence into agent beliefs.

    Validates projection checksums, not trusted source identity. There is no
    time synchronization or external-state materialization.
    """
    if not isinstance(engine, CausalEngine):
        raise EvidenceError("operator evidence frame requires a synthetic L2 engine")
    before = engine.state.digest()
    if not engine.evidence()["ledger_valid"]:
        raise EvidenceError("local kernel evidence is not chain-consistent")
    supported = {
        "gumas.unified.ace_identity_reference.p1",
        "gumas.unified.phase9_ledger_reference.p1",
        "gumas.unified.phase9_acceptance_reference.p1",
    }
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in projections:
        view = _object(raw, "external projection")
        name = view.get("schema")
        if name not in supported or name in seen:
            raise EvidenceError("unknown or duplicate external observation")
        if view.get("authority") not in (
            "unverified_external_observation_only", "external_acceptance_claim_only"):
            raise EvidenceError("external authority assertion refused")
        digest = _sha(view.get("projection_sha256"), "projection digest")
        if digest != canonical_sha256({k: v for k, v in view.items()
                                      if k != "projection_sha256"}):
            raise EvidenceError("external projection mutated after validation")
        seen.add(name)
        records.append(deepcopy(dict(view)))
    records.sort(key=lambda row: row["schema"])
    after = engine.state.digest()
    if before != after:
        raise AssertionError("evidence-frame inspection mutated L2")
    return {
        "schema": "gumas.unified.operator_evidence_frame.p1",
        "authority": "read_only_not_agent_knowledge",
        "local_run_id": engine.run_id,
        "local_state_sha256": before,
        "local_simulation_time_s": engine.state.time_s,
        "external_projections": records,
        "external_clock_aligned": False,
        "external_identity_promoted": False,
        "canonical_mutation_permitted": False,
    }
