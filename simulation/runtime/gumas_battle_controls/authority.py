"""Fail-closed execution-authority preflight for Phase-11 controls and Run 0.

Authority is a committed, hash-sealed record of an owner decision. The
preflight is a pure function of that record, the requested capability, the
requested scope, and a caller-supplied ``as_of`` date: it reads no wall clock
and never executes a macrostep. A refusal returns a receipt and discloses no
simulation outcome.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Mapping

from .constants import (
    AUTHORITY_SCHEMA,
    CAPABILITIES,
    HISTORICAL_CANON_STATUS,
    PHASE11_CONTRACT_ID,
    PHASE11_VERSION,
    REFUSAL_RECEIPT_SCHEMA,
    SCOPE_BASELINE_ID,
    SCOPE_BASELINE_VERSION,
    SCOPE_REPOSITORY,
)
from .identity import Phase11Error, hash_without_field

AUTHORITY_FIELDS = frozenset(
    {
        "schema",
        "authority_id",
        "phase11_contract_id",
        "granted_by",
        "granted_on",
        "expires_on",
        "evidence",
        "capabilities",
        "scope",
        "canon_promotion_authorized",
        "publication_authorized",
        "authority_sha256",
    }
)
SCOPE_FIELDS = frozenset({"repository", "baseline_id", "baseline_version"})


def _date(value: Any, label: str) -> _dt.date:
    if not isinstance(value, str):
        raise Phase11Error(f"{label} must be an ISO date string")
    try:
        return _dt.date.fromisoformat(value)
    except ValueError as exc:
        raise Phase11Error(f"{label} is not an ISO date: {value!r}") from exc


def expected_scope() -> dict[str, str]:
    return {
        "repository": SCOPE_REPOSITORY,
        "baseline_id": SCOPE_BASELINE_ID,
        "baseline_version": SCOPE_BASELINE_VERSION,
    }


def seal_authority(record: Mapping[str, Any]) -> dict[str, Any]:
    sealed = {key: value for key, value in record.items() if key != "authority_sha256"}
    sealed["authority_sha256"] = hash_without_field(sealed, "authority_sha256")
    return sealed


def _structure_reason(authority: Any) -> str | None:
    if authority is None:
        return "execution authority absent"
    if not isinstance(authority, Mapping):
        return "execution authority is not a mapping"
    if set(authority) != AUTHORITY_FIELDS:
        return "execution authority fields invalid"
    if authority.get("schema") != AUTHORITY_SCHEMA:
        return "unsupported execution authority schema"
    if authority.get("phase11_contract_id") != PHASE11_CONTRACT_ID:
        return "execution authority names a different contract"
    if str(authority.get("authority_sha256") or "") != hash_without_field(authority, "authority_sha256"):
        return "execution authority hash mismatch"
    return None


def _grant_reason(authority: Mapping[str, Any], capability: str) -> str | None:
    scope = authority.get("scope")
    if not isinstance(scope, Mapping) or set(scope) != SCOPE_FIELDS or dict(scope) != expected_scope():
        return "execution authority scope mismatch"
    capabilities = authority.get("capabilities")
    if not isinstance(capabilities, list) or not set(capabilities) <= CAPABILITIES:
        return "execution authority capabilities invalid"
    if capability not in capabilities:
        return f"execution authority lacks capability: {capability}"
    if authority.get("canon_promotion_authorized") is not False:
        return "execution authority must not authorize canon promotion"
    evidence = authority.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        return "execution authority lacks owner evidence"
    return None


def _window_reason(authority: Mapping[str, Any], as_of: str) -> str | None:
    try:
        granted = _date(authority.get("granted_on"), "granted_on")
        expires = _date(authority.get("expires_on"), "expires_on")
        today = _date(as_of, "as_of")
    except Phase11Error as exc:
        return str(exc)
    if today < granted:
        return "execution authority not yet in effect"
    if today > expires:
        return "execution authority expired"
    return None


def _check(authority: Any, capability: str, as_of: str) -> str | None:
    """Return a refusal reason, or None when execution is authorized."""
    if capability not in CAPABILITIES:
        return f"unknown capability: {capability}"
    return (
        _structure_reason(authority)
        or _grant_reason(authority, capability)
        or _window_reason(authority, as_of)
    )


def refusal_receipt(authority: Any, capability: str, as_of: str, reason: str) -> dict[str, Any]:
    authority_sha = authority.get("authority_sha256") if isinstance(authority, Mapping) else None
    receipt: dict[str, Any] = {
        "schema": REFUSAL_RECEIPT_SCHEMA,
        "phase11_contract_id": PHASE11_CONTRACT_ID,
        "phase11_version": PHASE11_VERSION,
        "historical_canon_status": HISTORICAL_CANON_STATUS,
        "requested_capability": capability,
        "as_of": as_of,
        "presented_authority_sha256": authority_sha,
        "refused": True,
        "reason": reason,
        "macrosteps_executed": 0,
        "outcome_disclosed": False,
        "run0_executed": False,
    }
    receipt["refusal_receipt_sha256"] = hash_without_field(receipt, "refusal_receipt_sha256")
    return receipt


def preflight(authority: Any, capability: str, as_of: str) -> dict[str, Any]:
    """Return ``{"authorized": True, ...}`` or ``{"authorized": False, "refusal": receipt}``."""
    reason = _check(authority, capability, as_of)
    if reason is not None:
        return {"authorized": False, "refusal": refusal_receipt(authority, capability, as_of, reason)}
    return {
        "authorized": True,
        "capability": capability,
        "as_of": as_of,
        "authority_sha256": str(authority["authority_sha256"]),
        "authority_id": str(authority["authority_id"]),
    }


def require(authority: Any, capability: str, as_of: str) -> dict[str, Any]:
    result = preflight(authority, capability, as_of)
    if not result["authorized"]:
        raise Phase11Error(result["refusal"]["reason"])
    return result
