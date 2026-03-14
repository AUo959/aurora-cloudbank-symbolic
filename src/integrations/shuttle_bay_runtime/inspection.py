"""Preflight and postflight inspection helpers for Shuttle Bay missions."""

from __future__ import annotations

from typing import Any, Dict, List

from src.integrations.shuttle_bay_runtime.models import CatalogBundle, InspectionResult, PolicyDecision, RoutingAssignment
from src.integrations.shuttle_bay_runtime.policy import security_layers_active
from src.integrations.shuttle_bay_runtime.routing import shuttle_exists


def _check(name: str, ok: bool, detail: str) -> Dict[str, Any]:
    return {"name": name, "ok": ok, "detail": detail}


def _max_concurrent_missions(catalog: CatalogBundle) -> int:
    payload = catalog.l1_config.get("l1_command_node", {})
    return int(payload.get("fleet_control", {}).get("max_concurrent_missions", 8) or 8)


def run_preflight_inspection(
    tool_name: str,
    policy: PolicyDecision,
    routing: RoutingAssignment,
    catalog: CatalogBundle,
    tools_registry: Dict[str, Dict[str, Any]],
    active_missions: int,
) -> InspectionResult:
    checks: List[Dict[str, Any]] = []
    issues: List[str] = []

    anchor_available = bool(catalog.bridge_core.get("anchor_seed"))
    checks.append(_check("anchor_available", anchor_available, "Bridge anchor seed is present." if anchor_available else "Bridge anchor seed is missing."))
    if not anchor_available:
        issues.append("Bridge anchor seed is missing.")

    security_active = security_layers_active(catalog.bridge_core)
    checks.append(_check("security_layers_active", security_active, "Bridge security layers are active." if security_active else "Bridge security layers are not fully active."))
    if not security_active and policy.lane.value == "red":
        issues.append("Bridge security layers are not fully active.")

    tool_registered = tool_name in tools_registry
    checks.append(_check("tool_registered", tool_registered, "Tool is registered in agent mode." if tool_registered else "Tool is not registered in agent mode."))
    if not tool_registered:
        issues.append(f"Tool '{tool_name}' is not registered.")

    tool_schema_present = bool(tools_registry.get(tool_name, {}).get("parameters"))
    checks.append(_check("tool_schema_available", tool_schema_present, "Tool schema is available." if tool_schema_present else "Tool schema is unavailable."))
    if not tool_schema_present:
        issues.append(f"Tool schema for '{tool_name}' is unavailable.")

    routing_loaded = catalog.source_status.get("tool_routing", {}).get("loaded", False)
    policy_loaded = catalog.source_status.get("policy_matrix", {}).get("loaded", False)
    checks.append(_check("routing_overlay_loaded", routing_loaded, "Tool routing overlay is loaded." if routing_loaded else "Tool routing overlay is unavailable."))
    checks.append(_check("policy_overlay_loaded", policy_loaded, "Policy matrix overlay is loaded." if policy_loaded else "Policy matrix overlay is unavailable."))
    if not routing_loaded:
        issues.append("Tool routing overlay is unavailable.")
    if not policy_loaded:
        issues.append("Policy matrix overlay is unavailable.")

    shuttle_ready = shuttle_exists(routing.shuttle_id, catalog)
    checks.append(_check("shuttle_resolved", shuttle_ready, f"Shuttle '{routing.shuttle_id}' is present in the fleet manifest." if shuttle_ready else f"Shuttle '{routing.shuttle_id}' is not present in the fleet manifest."))
    if not shuttle_ready:
        issues.append(f"Shuttle '{routing.shuttle_id}' is not present in the fleet manifest.")

    mission_limit = _max_concurrent_missions(catalog)
    capacity_available = active_missions < mission_limit
    checks.append(_check("mission_capacity", capacity_available, f"Active missions {active_missions}/{mission_limit} are within limit." if capacity_available else f"Mission capacity exceeded ({active_missions}/{mission_limit})."))
    if not capacity_available:
        issues.append(f"Mission capacity exceeded ({active_missions}/{mission_limit}).")

    checks.append(
        _check(
            "policy_classification",
            True,
            f"Tool domain={policy.tool_domain}, lane={policy.lane.value}, external={policy.external}, destructive={policy.destructive}.",
        )
    )

    if policy.deny_reasons:
        issues.extend(policy.deny_reasons)

    ok = not issues and policy.lane.value != "red"
    summary = "Preflight checks passed." if ok else "; ".join(dict.fromkeys(issues))
    return InspectionResult(ok=ok, stage="preflight", checks=checks, issues=list(dict.fromkeys(issues)), summary=summary)


def run_postflight_inspection(
    policy: PolicyDecision,
    routing: RoutingAssignment,
    execution_result: Dict[str, Any],
) -> InspectionResult:
    checks: List[Dict[str, Any]] = []
    issues: List[str] = []

    execution_success = bool(execution_result.get("success", False))
    checks.append(_check("execution_success", execution_success, "Underlying tool execution completed successfully." if execution_success else "Underlying tool execution returned an error response."))

    symbolic_hash_ok = bool(execution_result.get("symbolic_hash_validation", execution_success))
    checks.append(_check("symbolic_hash_validation", symbolic_hash_ok, "Symbolic hash validation is present." if symbolic_hash_ok else "Symbolic hash validation is absent."))
    if not symbolic_hash_ok:
        issues.append("Symbolic hash validation is absent.")

    review_flag = policy.review_required
    sanitization_summary = "Review flag preserved for downstream inspection." if review_flag else "No additional sanitization required."
    if not execution_success:
        sanitization_summary = "Execution error captured for audit replay."

    checks.append(_check("oversight_glyphs_attached", True, f"Oversight glyphs attached: {', '.join(routing.oversight_glyphs) or 'none'}"))
    checks.append(_check("sanitization_summary", True, sanitization_summary))

    summary = "Postflight audit complete." if execution_success else "Postflight audit captured an execution error."
    return InspectionResult(ok=execution_success, stage="postflight", checks=checks, issues=issues, summary=summary)
