#!/usr/bin/env python3
"""Validate Aurora L1 institutional-assurance event envelopes.

The validator uses only the Python standard library so the classification
boundary can be checked in minimal control-plane environments.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Literal

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = (
    REPO_ROOT
    / "docs"
    / "security"
    / "contracts"
    / "AURORA_L1__CONTRACT__INSTITUTIONAL_ASSURANCE_EVENT__v1.0__2026-07-27.json"
)

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


def _resolve_controlled_path(
    path: Path,
    *,
    allowed_root: Path = REPO_ROOT,
    expected: Literal["file", "directory"] = "file",
) -> Path:
    """Resolve a CLI-controlled path inside an explicit trust root."""
    root = allowed_root.resolve(strict=True)
    candidate = path if path.is_absolute() else Path.cwd() / path
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escapes controlled root {root}: {path}") from exc

    matches_expected_type = resolved.is_file() if expected == "file" else resolved.is_dir()
    if not matches_expected_type:
        raise ValueError(f"expected {expected} path: {resolved}")
    return resolved


def _read_json_object(path: Path, *, allowed_root: Path = REPO_ROOT) -> dict[str, Any]:
    controlled_path = _resolve_controlled_path(path, allowed_root=allowed_root)
    value = json.loads(controlled_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{controlled_path} root must be a JSON object")
    return value


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    return _read_json_object(path)


def canonical_event_digest(event: dict[str, Any]) -> str:
    payload = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _require_mapping(value: Any, name: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{name} must be an object")
        return {}
    return value


def _require_nonempty_string(value: Any, name: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{name} must be a non-empty string")


def _validate_revision(
    event: dict[str, Any],
    contract: dict[str, Any],
    prior_event: dict[str, Any] | None,
    errors: list[str],
) -> None:
    revision = event.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append("revision must be an integer >= 1")
        return

    previous_digest = event.get("previous_event_digest")
    if revision == 1:
        if previous_digest is not None:
            errors.append("revision 1 must set previous_event_digest to null")
        if prior_event is not None:
            errors.append("revision 1 must not be validated against a prior event")
        return

    if prior_event is None:
        errors.append("revision > 1 requires --prior-event / prior_event evidence")
        return

    prior_revision = prior_event.get("revision")
    if not isinstance(prior_revision, int) or revision != prior_revision + 1:
        errors.append("revision must increment the prior event revision by exactly 1")

    expected_digest = canonical_event_digest(prior_event)
    if previous_digest != expected_digest:
        errors.append("previous_event_digest does not match the canonical prior-event digest")

    for field in contract["immutable_revision_fields"]:
        if event.get(field) != prior_event.get(field):
            errors.append(f"immutable revision field changed: {field}")


def _resolve_evidence_path(reference: str, evidence_root: Path) -> Path | None:
    root = evidence_root.resolve()
    candidate = (root / reference).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _validate_external_verification(
    event: dict[str, Any],
    contract: dict[str, Any],
    evidence_root: Path | None,
    evidence: list[dict[str, Any]],
    errors: list[str],
) -> None:
    verification = _require_mapping(
        event.get("external_verification"), "external_verification", errors
    )
    for field in contract["external_verification_required"]:
        _require_nonempty_string(
            verification.get(field), f"external_verification.{field}", errors
        )

    method = verification.get("verification_method")
    if method not in contract["enums"]["external_verification_method"]:
        errors.append("external_verification.verification_method is not supported")

    if evidence_root is None:
        errors.append("Gate-001B validation requires evidence_root to resolve external evidence")
        return

    external_items = [
        item for item in evidence if item.get("origin") == "external_primary_evidence"
    ]
    for index, item in enumerate(external_items):
        reference = item.get("reference")
        digest = item.get("sha256")
        if not isinstance(reference, str) or not reference.strip():
            continue
        if not isinstance(digest, str) or not DIGEST_RE.fullmatch(digest):
            errors.append(
                f"external evidence {index} must include a 64-character lowercase sha256"
            )
            continue
        resolved = _resolve_evidence_path(reference, evidence_root)
        if resolved is None:
            errors.append(f"external evidence {index} escapes evidence_root")
            continue
        if not resolved.is_file():
            errors.append(f"external evidence {index} does not resolve to a file")
            continue
        observed = hashlib.sha256(resolved.read_bytes()).hexdigest()
        if observed != digest:
            errors.append(f"external evidence {index} sha256 does not match resolved file")


def validate_event(
    event: dict[str, Any],
    contract: dict[str, Any] | None = None,
    *,
    prior_event: dict[str, Any] | None = None,
    evidence_root: Path | None = None,
) -> list[str]:
    """Return validation errors; an empty list means the event conforms."""
    contract = contract or load_contract()
    errors: list[str] = []

    for field in contract["required_fields"]:
        if field not in event:
            errors.append(f"missing required field: {field}")

    enums = contract["enums"]
    for field in (
        "canon_status",
        "layer",
        "execution_mode",
        "evidence_authority",
        "data_treatment",
        "gate_track",
    ):
        value = event.get(field)
        if value not in enums[field]:
            errors.append(f"{field} must be one of {enums[field]!r}; got {value!r}")

    if event.get("data_treatment") != "first_class_operational_data":
        errors.append("institutional-assurance events must be first_class_operational_data")

    if event.get("substitutes_for_real_world_review") is not False:
        errors.append("substitutes_for_real_world_review must be false")

    mode = event.get("execution_mode")
    mode_rule = contract["mode_rules"].get(mode)
    if mode_rule:
        for field in (
            "evidence_authority",
            "gate_track",
            "real_world_interaction",
            "independent_external_assurance",
            "substitutes_for_real_world_review",
        ):
            if event.get(field) != mode_rule[field]:
                errors.append(
                    f"{field} must be {mode_rule[field]!r} for execution_mode {mode!r}"
                )

    _validate_revision(event, contract, prior_event, errors)

    provenance = _require_mapping(event.get("provenance"), "provenance", errors)
    for field in contract["provenance_required"]:
        _require_nonempty_string(provenance.get(field), f"provenance.{field}", errors)

    baseline = provenance.get("baseline_commit")
    if isinstance(baseline, str) and baseline and not SHA_RE.fullmatch(baseline):
        errors.append("provenance.baseline_commit must be a 40-character lowercase git SHA")

    if mode_rule and mode_rule["deterministic_required"]:
        if provenance.get("deterministic") is not True:
            errors.append("simulated institutional rehearsal must declare deterministic=true")
        if provenance.get("seed") in (None, ""):
            errors.append("simulated institutional rehearsal must record provenance.seed")

    roles = event.get("institutional_roles")
    if not isinstance(roles, list) or not roles:
        errors.append("institutional_roles must be a non-empty array")
        roles = []
    allowed_roles = set(mode_rule["allowed_role_representations"]) if mode_rule else set()
    for index, role in enumerate(roles):
        if not isinstance(role, dict):
            errors.append(f"institutional_roles[{index}] must be an object")
            continue
        _require_nonempty_string(role.get("role_id"), f"institutional_roles[{index}].role_id", errors)
        _require_nonempty_string(role.get("label"), f"institutional_roles[{index}].label", errors)
        representation = role.get("representation")
        if representation not in enums["role_representation"]:
            errors.append(
                f"institutional_roles[{index}].representation must be a recognized value"
            )
        elif allowed_roles and representation not in allowed_roles:
            errors.append(
                f"institutional_roles[{index}].representation {representation!r} "
                f"is not allowed for execution_mode {mode!r}"
            )

    raw_evidence = event.get("evidence_references")
    if not isinstance(raw_evidence, list) or not raw_evidence:
        errors.append("evidence_references must be a non-empty array")
        evidence: list[dict[str, Any]] = []
    else:
        evidence = []
        for index, item in enumerate(raw_evidence):
            if not isinstance(item, dict):
                errors.append(f"evidence_references[{index}] must be an object")
                continue
            evidence.append(item)
            _require_nonempty_string(
                item.get("reference"), f"evidence_references[{index}].reference", errors
            )
            if item.get("origin") not in enums["evidence_origin"]:
                errors.append(f"evidence_references[{index}].origin must be recognized")

    origins = {item.get("origin") for item in evidence}
    if mode_rule and mode_rule["required_evidence_origin"] not in origins:
        errors.append(
            f"execution_mode {mode!r} requires evidence origin "
            f"{mode_rule['required_evidence_origin']!r}"
        )

    if mode_rule and mode_rule.get("external_verification_required"):
        _validate_external_verification(event, contract, evidence_root, evidence, errors)

    _require_nonempty_string(event.get("event_id"), "event_id", errors)
    _require_nonempty_string(event.get("run_id"), "run_id", errors)

    return errors


def _load_json(path: Path, *, allowed_root: Path = REPO_ROOT) -> dict[str, Any]:
    return _read_json_object(path, allowed_root=allowed_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an Aurora L1 institutional-assurance event JSON file."
    )
    parser.add_argument("event", type=Path)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--prior-event", type=Path)
    parser.add_argument("--evidence-root", type=Path)
    args = parser.parse_args(argv)

    try:
        event = _load_json(args.event)
        contract = load_contract(args.contract)
        prior_event = _load_json(args.prior_event) if args.prior_event else None
        evidence_root = (
            _resolve_controlled_path(args.evidence_root, expected="directory")
            if args.evidence_root
            else None
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2

    errors = validate_event(
        event,
        contract,
        prior_event=prior_event,
        evidence_root=evidence_root,
    )
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
