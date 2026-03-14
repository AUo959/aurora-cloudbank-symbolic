"""Routing resolution for Shuttle Bay missions."""

from __future__ import annotations

from typing import Any, Dict, List

from src.integrations.shuttle_bay_runtime.models import CatalogBundle, RoutingAssignment


def normalize_label(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


def authority_title_from_key(key: str) -> str:
    return key.replace("_", " ").title()


def _integration_sequence(catalog: CatalogBundle) -> List[Dict[str, Any]]:
    payload = catalog.integration_config.get("l2_meta_agent_integration", {})
    return payload.get("l2_meta_agents", {}).get("integration_sequence", [])


def _authorization_matrix(catalog: CatalogBundle) -> Dict[str, Dict[str, Any]]:
    payload = catalog.integration_config.get("l2_meta_agent_integration", {})
    return payload.get("staff_authorization_matrix", {})


def _glyph_agents(catalog: CatalogBundle) -> Dict[str, str]:
    payload = catalog.integration_config.get("l2_meta_agent_integration", {})
    return payload.get("l3_symbolic_oversight", {}).get("glyph_agents", {})


def find_authority_key(authority_role: str, catalog: CatalogBundle) -> str:
    matrix = _authorization_matrix(catalog)
    normalized_role = normalize_label(authority_role)
    for key in matrix:
        if normalize_label(authority_title_from_key(key)) == normalized_role:
            return key
    return ""


def find_relay_record(relay_agent: str, catalog: CatalogBundle) -> Dict[str, Any]:
    normalized_agent = normalize_label(relay_agent)
    for item in _integration_sequence(catalog):
        if normalize_label(str(item.get("agent", ""))) == normalized_agent:
            return item
    return {}


def shuttle_exists(shuttle_id: str, catalog: CatalogBundle) -> bool:
    shuttles = catalog.fleet_manifest.get("fleet_manifest", {}).get("shuttles", {})
    return shuttle_id in shuttles


def resolve_routing_assignment(tool_name: str, catalog: CatalogBundle) -> RoutingAssignment:
    routing_table = catalog.tool_routing.get("tool_routing", {})
    entry = routing_table.get(tool_name)
    if not entry:
        raise ValueError(f"No shuttle-bay routing entry configured for tool '{tool_name}'")

    authority_role = str(entry.get("authority_role", "")).strip()
    relay_agent = str(entry.get("relay_agent", "")).strip()
    authority_key = find_authority_key(authority_role, catalog)
    relay_record = find_relay_record(relay_agent, catalog)
    clearance_required = str(
        relay_record.get("clearance_required")
        or entry.get("clearance_required")
        or _authorization_matrix(catalog).get(authority_key, {}).get("clearance", "")
    ).strip()

    assignment = RoutingAssignment(
        tool_name=tool_name,
        tool_domain=str(entry.get("tool_domain", "unknown")),
        shuttle_id=str(entry.get("shuttle_id", "")),
        relay_agent=relay_agent,
        authority_role=authority_role,
        authority_key=authority_key,
        clearance_required=clearance_required,
        oversight_glyphs=list(entry.get("oversight_glyphs", [])),
        lane_hint=str(entry.get("lane", "")),
    )

    return assignment


def routing_annotations(tool_name: str, catalog: CatalogBundle) -> Dict[str, Any]:
    assignment = resolve_routing_assignment(tool_name, catalog)
    glyph_map = _glyph_agents(catalog)
    return {
        "assignment": assignment,
        "oversight_functions": {glyph: glyph_map.get(glyph, "") for glyph in assignment.oversight_glyphs},
        "shuttle_exists": shuttle_exists(assignment.shuttle_id, catalog),
    }
