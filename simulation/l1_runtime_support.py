#!/usr/bin/env python3
"""Validation, git, and persistence helpers for the governed Orion L1 runtime."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class PreflightError(RuntimeError):
    """Raised when L1 cannot safely enter INIT."""


class GovernanceError(RuntimeError):
    """Raised when an actionable mutation lacks complete Triplex authorization."""


def evaluate_preflight(
    baseline: Dict[str, Any],
    population: Any,
    provenance_path: Path,
    *,
    run_created: bool,
) -> Dict[str, Any]:
    """Evaluate INIT gates without creating or advancing a run."""
    blockers: List[str] = []
    warnings: List[str] = []
    _check_staff_authority(baseline, provenance_path, blockers)
    _check_pilot_boundary(baseline, blockers)
    _check_population(population, blockers, warnings)
    _check_locus_quarantine(baseline, blockers)
    _check_legacy_and_benchmark(baseline, blockers)
    _check_governance(baseline, blockers)
    return {
        "ready": not blockers,
        "blockers": blockers,
        "warnings": warnings,
        "tick": 0,
        "run_created": run_created,
        "runtime_contract_version": baseline["runtime_contract_version"],
    }


def _check_staff_authority(
    baseline: Dict[str, Any],
    provenance_path: Path,
    blockers: List[str],
) -> None:
    authority = baseline.get("authority", {})
    _check_staff_registry_config(authority.get("staff_registry", {}), blockers)
    expected_revision = _expected_canonrec_revision(authority, blockers)
    provenance = _load_canon_provenance(provenance_path, blockers)
    if provenance is None:
        return
    receipt = _staff_authority_receipt(provenance, blockers)
    if receipt is not None:
        _check_staff_authority_receipt(receipt, expected_revision, blockers)


def _check_staff_registry_config(
    staff: Dict[str, Any],
    blockers: List[str],
) -> None:
    if staff.get("status") != "resolved_authority_boundary":
        blockers.append("staff registry authority boundary is unresolved")
    if staff.get("authority_repository") != "AUo959/CanonRec":
        blockers.append("CanonRec is not configured as staff canon authority")


def _expected_canonrec_revision(
    authority: Dict[str, Any],
    blockers: List[str],
) -> Optional[str]:
    expected_revision = authority.get("canonrec", {}).get("revision")
    if not is_git_sha(expected_revision):
        blockers.append("L1 baseline does not pin a valid CanonRec revision")
        return None
    return expected_revision


def _load_canon_provenance(
    provenance_path: Path,
    blockers: List[str],
) -> Optional[Dict[str, Any]]:
    try:
        return read_json(provenance_path)
    except (OSError, ValueError):
        blockers.append("canon provenance receipt is unavailable or invalid")
        return None


def _staff_authority_receipt(
    provenance: Dict[str, Any],
    blockers: List[str],
) -> Optional[Dict[str, Any]]:
    if provenance.get("unreconciled_surfaces"):
        blockers.append("canon provenance still reports unreconciled surfaces")
    staff_receipts = [
        item
        for item in provenance.get("resolved_surfaces", [])
        if item.get("name") == "orion_station_staff_registry"
    ]
    if len(staff_receipts) != 1:
        blockers.append("canon provenance lacks one resolved staff authority receipt")
        return None
    return staff_receipts[0]


def _check_staff_authority_receipt(
    receipt: Dict[str, Any],
    expected_revision: Optional[str],
    blockers: List[str],
) -> None:
    if receipt.get("authority_repository") != "AUo959/CanonRec":
        blockers.append("canon provenance does not assign staff authority to CanonRec")
    if receipt.get("cloudbank_role") != "runtime_projection_non_authoritative":
        blockers.append("CloudBank staff registry is not typed as a runtime projection")
    if receipt.get("authority_revision") != expected_revision:
        blockers.append("staff authority revision does not match the L1 baseline")


def _check_pilot_boundary(
    baseline: Dict[str, Any],
    blockers: List[str],
) -> None:
    pilot = baseline.get("pilot_boundary", {})
    if pilot.get("residency") != "Earth" or pilot.get("l1_entity") is not False:
        blockers.append("Pilot boundary would permit L1 embodiment")
    if pilot.get("implicit_station_command_authority") is not False:
        blockers.append("Pilot role incorrectly implies station command authority")


def _check_population(
    population: Any,
    blockers: List[str],
    warnings: List[str],
) -> None:
    if population.missing_named_human_claim:
        blockers.append("false missing-human claim is active")
    if population.current_human_crew_complement is None:
        warnings.append(
            "exact current human crew complement is unresolved and quarantined"
        )


def _check_locus_quarantine(
    baseline: Dict[str, Any],
    blockers: List[str],
) -> None:
    locus = baseline.get("orbital_locus", {})
    if locus.get("status") != "quarantined_conflict":
        blockers.append("orbital locus conflict is not safely quarantined")
    if not locus.get("prohibited_causal_derivations"):
        blockers.append("orbital locus quarantine lacks causal-use restrictions")


def _check_legacy_and_benchmark(
    baseline: Dict[str, Any],
    blockers: List[str],
) -> None:
    legacy = baseline.get("legacy_state", {})
    if legacy.get("genesis_authority") is not False:
        blockers.append(
            "legacy SIMULATION_STATE is still eligible as genesis authority"
        )
    benchmark = baseline.get("benchmark", {})
    if (
        benchmark.get("canonical_component")
        != "simulation/orion_station_simulation_v2.py"
    ):
        blockers.append("canonical benchmark is not wired to Orion simulation v2")
    if "not the live L1 world runtime" not in benchmark.get("role", ""):
        blockers.append(
            "historical benchmark is being conflated with the live L1 runtime"
        )


def _check_governance(
    baseline: Dict[str, Any],
    blockers: List[str],
) -> None:
    governance = baseline.get("governance", {})
    if governance.get("ethics_protocol") != "Picard_Delta_3":
        blockers.append(
            "Picard_Delta_3 governance is not active in the runtime contract"
        )
    if governance.get("actionable_event_policy") != "explicit_triplex_receipt_required":
        blockers.append("actionable events do not fail closed on Triplex authorization")


def read_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def required_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


def optional_int(value: Any, name: str) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer or null")
    return value


def required_bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a boolean")
    return value


def int_mapping(value: Any, name: str) -> Dict[str, int]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    result: Dict[str, int] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{name} keys must be non-empty strings")
        result[key] = required_int(item, f"{name}.{key}")
    return result


def string_mapping(value: Any, name: str) -> Dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    result: Dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{name} keys must be non-empty strings")
        if not isinstance(item, str):
            raise ValueError(f"{name}.{key} must be a string")
        result[key] = item
    return result


def is_git_sha(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(char in "0123456789abcdefABCDEF" for char in value)
    )


def validate_revision(value: str, field_name: str) -> None:
    if not is_git_sha(value):
        raise ValueError(f"{field_name} must be a 40-character git SHA")


def resolve_cloudbank_revision(project_root: Path) -> str:
    """Resolve a checked-out git SHA without executing a subprocess."""
    git_dir = _git_directory(project_root)
    head = _read_text(git_dir / "HEAD", "unable to read CloudBank git HEAD")
    if is_git_sha(head):
        return head.lower()
    ref_name = _head_reference(head)
    revision = _read_git_reference(git_dir, ref_name)
    validate_revision(revision, "cloudbank_revision")
    return revision.lower()


def _git_directory(project_root: Path) -> Path:
    git_dir = project_root / ".git"
    if not git_dir.is_dir():
        raise PreflightError(
            "unable to pin CloudBank git revision: .git directory missing"
        )
    return git_dir


def _read_text(path: Path, error: str) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise PreflightError(error) from exc


def _head_reference(head: str) -> str:
    if not head.startswith("ref: "):
        raise PreflightError("CloudBank git HEAD has unsupported format")
    ref_name = head.removeprefix("ref: ").strip()
    if not _safe_git_ref(ref_name):
        raise PreflightError("CloudBank git HEAD contains an unsafe ref")
    return ref_name


def _read_git_reference(git_dir: Path, ref_name: str) -> str:
    loose_ref = git_dir / ref_name
    if loose_ref.is_file():
        return _read_text(loose_ref, "unable to read CloudBank git reference")
    return _read_packed_reference(git_dir / "packed-refs", ref_name)


def _read_packed_reference(packed_refs: Path, ref_name: str) -> str:
    if not packed_refs.is_file():
        raise PreflightError("unable to resolve CloudBank git HEAD reference")
    for line in packed_refs.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith(("#", "^")):
            continue
        revision, separator, packed_ref = line.partition(" ")
        if separator and packed_ref == ref_name:
            return revision
    raise PreflightError("unable to resolve CloudBank git HEAD reference")


def _safe_git_ref(ref_name: str) -> bool:
    if not ref_name.startswith("refs/"):
        return False
    if ref_name.startswith("/") or ".." in ref_name or "\\" in ref_name:
        return False
    return all(part not in {"", ".", ".."} for part in ref_name.split("/"))


def event_for_roll(roll: float) -> tuple[str, str]:
    if roll < 0.30:
        return (
            "routine_shift_handoff",
            "Routine station shift handoff completed without material exception.",
        )
    if roll < 0.50:
        return (
            "maintenance_queue_progress",
            "A scheduled maintenance queue advanced within standing-authority limits.",
        )
    if roll < 0.65:
        return (
            "research_queue_progress",
            "A research work queue advanced; no canon-level conclusion was generated.",
        )
    return (
        "no_material_event",
        "No material station event was recorded for this advancement window.",
    )


def export_run_state(state: Any) -> Dict[str, Any]:
    return {
        "manifest": {
            **asdict(state.manifest),
            "population": asdict(state.manifest.population),
        },
        "world_state": state.world_state,
        "character_knowledge": {
            key: [asdict(record) for record in records]
            for key, records in state.character_knowledge.items()
        },
        "station_records": [asdict(record) for record in state.station_records],
        "runtime_observations": [
            asdict(record) for record in state.runtime_observations
        ],
        "pilot_knowledge": [asdict(record) for record in state.pilot_knowledge],
        "communications": state.communications,
        "events": state.events,
        "promotion_candidates": state.promotion_candidates,
    }


def persist_run_state(state: Any, run_root: Path) -> None:
    run_dir = run_root / state.manifest.run_id
    run_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    destination = run_dir / "state.json"
    payload = json.dumps(export_run_state(state), indent=2, sort_keys=True) + "\n"
    temporary_path = _write_temporary_state(run_dir, payload)
    try:
        os.replace(temporary_path, destination)
        os.chmod(destination, 0o600)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _write_temporary_state(run_dir: Path, payload: str) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=".state-",
        suffix=".tmp",
        dir=run_dir,
        delete=False,
    ) as temporary:
        os.chmod(temporary.name, 0o600)
        temporary.write(payload)
        temporary.flush()
        os.fsync(temporary.fileno())
        return Path(temporary.name)


def resolve_run_root(path: Path, project_root: Path) -> Path:
    resolved = path.expanduser().resolve()
    project = project_root.resolve()
    if resolved == project or project in resolved.parents:
        raise PreflightError("run persistence must remain outside the repository")
    resolved.mkdir(mode=0o700, parents=True, exist_ok=True)
    return resolved


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
