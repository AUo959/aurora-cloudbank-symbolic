"""Resource builders for Shuttle Bay MCP resource exposure."""

from __future__ import annotations

from typing import Any, Dict, List

from src.integrations.shuttle_bay_runtime.models import CatalogBundle


MANIFEST_RESOURCE_URI = "aurora://mcp-shuttle-bay/manifest"
FLEET_RESOURCE_URI = "aurora://mcp-shuttle-bay/fleet"
AUTHORITIES_RESOURCE_URI = "aurora://mcp-shuttle-bay/authorities"
TOOL_ROUTING_RESOURCE_URI = "aurora://mcp-shuttle-bay/tool-routing"
POLICY_RESOURCE_URI = "aurora://mcp-shuttle-bay/policy"

RESOURCE_DEFINITIONS = [
    {
        "uri": MANIFEST_RESOURCE_URI,
        "name": "Aurora MCP Shuttle Bay Manifest",
        "description": "Structured manifest for Aurora's Shuttle Bay integration surface.",
        "mimeType": "application/json",
    },
    {
        "uri": FLEET_RESOURCE_URI,
        "name": "Aurora Shuttle Bay Fleet Registry",
        "description": "Fleet registry data exposed as read-only Shuttle Bay context.",
        "mimeType": "application/json",
    },
    {
        "uri": AUTHORITIES_RESOURCE_URI,
        "name": "Aurora Shuttle Bay Authorities",
        "description": "Authority and relay mappings derived from the integration canon.",
        "mimeType": "application/json",
    },
    {
        "uri": TOOL_ROUTING_RESOURCE_URI,
        "name": "Aurora Shuttle Bay Tool Routing",
        "description": "Tool-to-domain, relay, and shuttle mapping overlay for the Shuttle Bay runtime.",
        "mimeType": "application/json",
    },
    {
        "uri": POLICY_RESOURCE_URI,
        "name": "Aurora Shuttle Bay Policy Matrix",
        "description": "Deterministic policy and lane mapping overlay for Shuttle Bay mission handling.",
        "mimeType": "application/json",
    },
]


def list_resource_definitions() -> Dict[str, List[Dict[str, Any]]]:
    return {"resources": list(RESOURCE_DEFINITIONS)}


def resource_uris() -> List[str]:
    return [item["uri"] for item in RESOURCE_DEFINITIONS]


def build_authorities_resource(catalog: CatalogBundle) -> Dict[str, Any]:
    payload = catalog.integration_config.get("l2_meta_agent_integration", {})
    return {
        "staff_authorization_matrix": payload.get("staff_authorization_matrix", {}),
        "integration_sequence": payload.get("l2_meta_agents", {}).get("integration_sequence", []),
        "glyph_agents": payload.get("l3_symbolic_oversight", {}).get("glyph_agents", {}),
    }


def build_fleet_resource(catalog: CatalogBundle) -> Dict[str, Any]:
    return catalog.fleet_manifest.get("fleet_manifest", {})


def build_tool_routing_resource(catalog: CatalogBundle) -> Dict[str, Any]:
    return catalog.tool_routing


def build_policy_resource(catalog: CatalogBundle) -> Dict[str, Any]:
    return catalog.policy_matrix


def read_resource_payload(uri: str, catalog: CatalogBundle, manifest: Dict[str, Any]) -> Dict[str, Any]:
    if uri == MANIFEST_RESOURCE_URI:
        return manifest
    if uri == FLEET_RESOURCE_URI:
        return build_fleet_resource(catalog)
    if uri == AUTHORITIES_RESOURCE_URI:
        return build_authorities_resource(catalog)
    if uri == TOOL_ROUTING_RESOURCE_URI:
        return build_tool_routing_resource(catalog)
    if uri == POLICY_RESOURCE_URI:
        return build_policy_resource(catalog)
    raise ValueError("Unknown resource URI")
