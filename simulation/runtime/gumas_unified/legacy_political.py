"""Read-only compatibility projection for the earlier GUMAS political snapshot.

This is deliberately NOT a state adapter and does not call or import the legacy
engine: legacy political scores are not conserved physical quantities.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def observe_legacy_political_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("factions"), dict):
        raise ValueError("expected a serialized GUMASState with factions map")
    polities: dict[str, dict[str, Any]] = {}
    for faction_id, faction in sorted(snapshot["factions"].items()):
        if not isinstance(faction_id, str) or not isinstance(faction, dict):
            raise ValueError("invalid legacy faction")
        # Legacy metrics are observations, never automatically real resources.
        metrics: dict[str, Any] = {}
        for field in ("economic_strength", "military_strength", "political_stability",
                      "social_cohesion", "trust_scores"):
            if field in faction:
                metrics[field] = deepcopy(faction[field])
        polities[faction_id] = metrics
    return {"kind": "legacy_political_observation",
            "authority": "noncanonical_read_only",
            "source_provenance": "GUMAS_SIM_2.5/SIM_ENGINE_OUTPUTS/models.py",
            "not_a_resource_ledger": True,
            "polities": polities}
