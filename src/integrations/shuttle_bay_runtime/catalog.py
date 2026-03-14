"""Catalog loading for Shuttle Bay mission policy and routing."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Tuple

from src.integrations.shuttle_bay_runtime.models import CatalogBundle


REPO_ROOT = Path(__file__).resolve().parents[3]

SOURCE_PATHS = {
    "bridge_core": REPO_ROOT / "modules" / "symbolic_core" / "mcp_bridge_core.json",
    "fleet_manifest": REPO_ROOT / "docs" / "operational" / "reports" / "fleet_manifest.json",
    "integration_config": REPO_ROOT / "docs" / "operational" / "guides" / "L2_META_AGENT_INTEGRATION_CONFIG.json",
    "l1_config": REPO_ROOT / "operations" / "command_center" / "l1_config.yaml",
    "staff_registry": REPO_ROOT / "docs" / "operational" / "reports" / "staff_registry.json",
    "tool_routing": REPO_ROOT / "config" / "shuttle_bay" / "tool_routing.json",
    "policy_matrix": REPO_ROOT / "config" / "shuttle_bay" / "policy_matrix.json",
}


def _load_json(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not path.exists():
        return {}, {"loaded": False, "path": str(path), "error": "missing"}
    try:
        return json.loads(path.read_text()), {"loaded": True, "path": str(path)}
    except Exception as exc:
        return {}, {"loaded": False, "path": str(path), "error": str(exc)}


def _bool_from_text(text: str, default: bool = False) -> bool:
    value = text.strip().lower()
    if value == "true":
        return True
    if value == "false":
        return False
    return default


def _int_from_match(pattern: str, text: str, default: int) -> int:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return default
    try:
        return int(match.group(1))
    except (TypeError, ValueError):
        return default


def _string_from_match(pattern: str, text: str, default: str) -> str:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return default
    return match.group(1).strip().strip("'\"")


def _load_l1_config(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not path.exists():
        return {}, {"loaded": False, "path": str(path), "error": "missing"}

    text = path.read_text()
    parser = "regex_fallback"

    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        parser = "yaml"
    except Exception:
        data = {
            "l1_command_node": {
                "fleet_control": {
                    "max_concurrent_missions": _int_from_match(r"max_concurrent_missions:\s*(\d+)", text, 8),
                    "preflight_mandatory": _bool_from_text(
                        _string_from_match(r"preflight_mandatory:\s*([A-Za-z]+)", text, "true"),
                        True,
                    ),
                },
                "security": {
                    "access_control": _string_from_match(r"access_control:\s*([A-Za-z0-9_'\"]+)", text, "rbac"),
                    "audit_logging": _bool_from_text(
                        _string_from_match(r"audit_logging:\s*([A-Za-z]+)", text, "true"),
                        True,
                    ),
                    "encryption_required": _bool_from_text(
                        _string_from_match(r"encryption_required:\s*([A-Za-z]+)", text, "true"),
                        True,
                    ),
                    "session_timeout": _int_from_match(r"session_timeout:\s*(\d+)", text, 3600),
                },
            }
        }

    return data, {"loaded": True, "path": str(path), "parser": parser}


def load_catalog_bundle() -> CatalogBundle:
    bridge_core, bridge_status = _load_json(SOURCE_PATHS["bridge_core"])
    fleet_manifest, fleet_status = _load_json(SOURCE_PATHS["fleet_manifest"])
    integration_config, integration_status = _load_json(SOURCE_PATHS["integration_config"])
    staff_registry, staff_status = _load_json(SOURCE_PATHS["staff_registry"])
    tool_routing, routing_status = _load_json(SOURCE_PATHS["tool_routing"])
    policy_matrix, policy_status = _load_json(SOURCE_PATHS["policy_matrix"])
    l1_config, l1_status = _load_l1_config(SOURCE_PATHS["l1_config"])

    return CatalogBundle(
        bridge_core=bridge_core,
        fleet_manifest=fleet_manifest,
        integration_config=integration_config,
        l1_config=l1_config,
        staff_registry=staff_registry,
        tool_routing=tool_routing,
        policy_matrix=policy_matrix,
        source_status={
            "bridge_core": bridge_status,
            "fleet_manifest": fleet_status,
            "integration_config": integration_status,
            "l1_config": l1_status,
            "staff_registry": staff_status,
            "tool_routing": routing_status,
            "policy_matrix": policy_status,
        },
    )
