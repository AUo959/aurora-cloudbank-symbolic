"""Policy evaluation for deterministic Shuttle Bay mission handling."""

from __future__ import annotations

from typing import Dict, Iterable, List

from src.integrations.shuttle_bay_runtime.models import CatalogBundle, PolicyDecision, TrustLane


def security_layers_active(bridge_core: Dict[str, object]) -> bool:
    layers = bridge_core.get("security_layers", {})
    if not isinstance(layers, dict):
        return False
    return (
        layers.get("drift_lock") == "ACTIVE"
        and layers.get("guardian_ring") in {"ACTIVE", "STAGED_ACTIVE"}
        and layers.get("ethics_lock") == "ENFORCED"
    )


def _lane_from_value(value: str) -> TrustLane:
    normalized = (value or "").strip().lower()
    if normalized == TrustLane.GREEN.value:
        return TrustLane.GREEN
    if normalized == TrustLane.GRAY.value:
        return TrustLane.GRAY
    return TrustLane.RED


def _policy_action_for_lane(lane: TrustLane) -> str:
    if lane == TrustLane.GREEN:
        return "allow"
    if lane == TrustLane.GRAY:
        return "review"
    return "deny"


def _evaluate_deny_conditions(
    deny_conditions: Iterable[str],
    catalog: CatalogBundle,
    tool_schema_present: bool,
) -> List[str]:
    reasons: List[str] = []
    for condition in deny_conditions:
        if condition == "missing_anchor" and not catalog.bridge_core.get("anchor_seed"):
            reasons.append("Bridge anchor seed is unavailable.")
        elif condition == "security_inactive" and not security_layers_active(catalog.bridge_core):
            reasons.append("Bridge security layers are not fully active.")
        elif condition == "missing_tool_schema" and not tool_schema_present:
            reasons.append("Tool schema is unavailable for Shuttle Bay preflight.")
        elif condition == "missing_overlay_config":
            if not catalog.source_status.get("tool_routing", {}).get("loaded", False) or not catalog.source_status.get(
                "policy_matrix", {}
            ).get("loaded", False):
                reasons.append("Shuttle Bay overlay policy or routing config is unavailable.")
    return reasons


def evaluate_policy_decision(
    tool_name: str,
    tool_domain: str,
    lane_hint: str,
    catalog: CatalogBundle,
    tool_schema_present: bool,
) -> PolicyDecision:
    policy_classes = catalog.policy_matrix.get("policy_classes", {})
    policy_entry = policy_classes.get(tool_domain)
    if not policy_entry:
        return PolicyDecision(
            tool_name=tool_name,
            tool_domain=tool_domain,
            lane=TrustLane.RED,
            risk_score=1.0,
            policy_action="deny",
            review_required=False,
            destructive=False,
            external=False,
            deny_reasons=[f"No Shuttle Bay policy configured for tool domain '{tool_domain}'."],
        )

    lane = _lane_from_value(lane_hint or str(policy_entry.get("default_lane", TrustLane.RED.value)))
    risk_score = float(policy_entry.get("risk_score", 1.0))
    review_required = bool(policy_entry.get("review_required", lane == TrustLane.GRAY))
    destructive = bool(policy_entry.get("destructive", False))
    external = bool(policy_entry.get("external", False))
    deny_reasons = _evaluate_deny_conditions(policy_entry.get("deny_conditions", []), catalog, tool_schema_present)

    if deny_reasons:
        lane = TrustLane.RED
        review_required = False

    return PolicyDecision(
        tool_name=tool_name,
        tool_domain=tool_domain,
        lane=lane,
        risk_score=risk_score,
        policy_action=_policy_action_for_lane(lane),
        review_required=review_required,
        destructive=destructive,
        external=external,
        deny_reasons=deny_reasons,
    )
