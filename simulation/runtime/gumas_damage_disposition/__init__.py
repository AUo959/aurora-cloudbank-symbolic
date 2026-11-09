"""Deterministic GUMAS Phase-7 damage/disposition runtime boundary."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from simulation.runtime.gumas_movement_geometry.kernel import (
    _hash_without_field as _movement_hash_without_field,
)

from . import kernel as _kernel
from .normalization import normalize_phase6_receipt, normalizer_source_identity

Phase7Error = _kernel.Phase7Error
_raw_step_phase7_state = _kernel.step_phase7_state


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def step_phase7_state(
    state: Mapping[str, Any], phase6_receipt: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate raw Phase-6 provenance, normalize semantic lists, then resolve damage."""
    try:
        normalized = normalize_phase6_receipt(phase6_receipt)
    except ValueError as exc:
        raise Phase7Error(str(exc)) from exc

    next_state, receipt = _raw_step_phase7_state(state, normalized)
    normalizer_identity = normalizer_source_identity()
    composite_payload = {
        "damage_core_source_identity": receipt["phase7_source_identity"],
        "semantic_normalizer_source_identity": normalizer_identity,
    }
    composite_sha = hashlib.sha256(_canonical_bytes(composite_payload)).hexdigest()

    next_state["phase7_semantic_normalizer_source_identity"] = normalizer_identity
    next_state["phase7_composite_source_sha256"] = composite_sha
    next_state["state_sha256"] = _movement_hash_without_field(next_state, "state_sha256")

    receipt["phase7_semantic_normalizer_source_identity"] = normalizer_identity
    receipt["phase7_composite_source_sha256"] = composite_sha
    receipt["next_state_sha256"] = next_state["state_sha256"]
    receipt["phase6_raw_receipt_validated_before_normalization"] = True
    receipt["phase7_receipt_sha256"] = _kernel._hash_without_field(
        receipt, "phase7_receipt_sha256"
    )
    return next_state, receipt


# Package initialization runs before direct submodule imports complete; patch the
# public kernel entry point so every caller receives the authoritative boundary.
_kernel.step_phase7_state = step_phase7_state

__all__ = ["Phase7Error", "step_phase7_state"]
