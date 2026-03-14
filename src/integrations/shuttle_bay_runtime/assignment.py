"""Symbolic assignment helpers for Shuttle Bay missions."""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.integrations.shuttle_bay_runtime.models import CatalogBundle, RoutingAssignment
from src.integrations.shuttle_bay_runtime.routing import authority_title_from_key, normalize_label


def _authorization_entry(catalog: CatalogBundle, authority_key: str) -> Dict[str, Any]:
    payload = catalog.integration_config.get("l2_meta_agent_integration", {})
    return payload.get("staff_authorization_matrix", {}).get(authority_key, {})


def _human_staff(catalog: CatalogBundle) -> Dict[str, Dict[str, Any]]:
    return catalog.staff_registry.get("crew_registry", {}).get("human_staff", {})


def _match_human_name(authority_role: str, catalog: CatalogBundle) -> Optional[str]:
    normalized_role = normalize_label(authority_role)
    for human in _human_staff(catalog).values():
        station_role = str(human.get("station_role", ""))
        station_role_title = station_role.replace("_", " ").replace("&", " ")
        if normalize_label(station_role_title) == normalized_role:
            return str(human.get("name", "")).strip() or None
    return None


def resolve_authority_name(assignment: RoutingAssignment, catalog: CatalogBundle) -> Optional[str]:
    authority_entry = _authorization_entry(catalog, assignment.authority_key)
    if authority_entry.get("name"):
        return str(authority_entry["name"]).strip() or None
    return _match_human_name(assignment.authority_role, catalog)


def build_assignment_metadata(assignment: RoutingAssignment, catalog: CatalogBundle) -> Dict[str, Any]:
    authority_entry = _authorization_entry(catalog, assignment.authority_key)
    authority_name = resolve_authority_name(assignment, catalog)
    return {
        "assignment_mode": "symbolic_role_first",
        "authority_role": assignment.authority_role or authority_title_from_key(assignment.authority_key),
        "authority_name": authority_name,
        "authority_key": assignment.authority_key,
        "relay_agent": assignment.relay_agent,
        "shuttle_id": assignment.shuttle_id,
        "clearance_required": assignment.clearance_required or authority_entry.get("clearance", ""),
        "human_assignment_confirmed": authority_name is not None,
    }
