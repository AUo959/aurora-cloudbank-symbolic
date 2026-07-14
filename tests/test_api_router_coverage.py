"""
Deterministic coverage validator for api/aurora_api.py's mounted routers
against docs/api/api_surface_inventory.json.

Complements tests/test_api_surface_inventory.py (structural/schema checks
on the inventory file alone) with a check that compares the inventory
against actual `app.include_router(...)` call sites in the primary app.
See issue #1204 — the structural test alone did not detect four routers
that were mounted but missing from the inventory (#1146); this test would
have caught that class of gap, and does catch one still-open instance of
it (memory_retrieval, fixed alongside this test in the same PR).

Scope, stated explicitly per #1204's own acceptance criteria:

- Covers `app.include_router(...)` call sites in api/aurora_api.py only —
  the "primary_fastapi_app" surface (id: primary_fastapi_app,
  entrypoint: api/aurora_api.py). This is `api.aurora_api:app` as a
  module-level object; there is no create_app() factory to target instead.
- Does NOT validate declared standalone/legacy/compatibility-bridge
  services (mesh_runtime_v1, pat_terminal_overlay, api_bridge_server,
  mesh_api_js, enhanced_api_bridge, generated_api_catalog_snapshot) —
  those aren't mounted on api.aurora_api:app, so there's no
  include_router() call site to check them against. They're covered only
  by test_api_surface_inventory.py's entrypoint-file-exists check. This is
  a real, acknowledged gap, not a silent omission.
- Framework/docs routes (/docs, /redoc, /openapi.json, /health, /ready,
  /live, /metrics) are defined directly on `app`, not via a named router
  variable passed to include_router(), so they never appear in the
  extracted symbol list and need no exception list.
"""

from pathlib import Path

from tests._api_router_coverage import extract_include_router_symbols

REPO_ROOT = Path(__file__).resolve().parents[1]
AURORA_API_PATH = REPO_ROOT / "api" / "aurora_api.py"
INVENTORY_PATH = REPO_ROOT / "docs" / "api" / "api_surface_inventory.json"

# Hand-verified mapping from each include_router() call-site argument
# (exact source text, as extracted by extract_include_router_symbols) to
# its docs/api/api_surface_inventory.json entry id. Verified against
# api/aurora_api.py on 2026-07-13 (issue #1204) by cross-referencing each
# router's originating module against each inventory entry's `entrypoint`.
#
# MEMORY_RETRIEVAL_ROUTER is included twice (two separate try/except
# blocks, apparently redundant — flagged in the PR description, not fixed
# here since that's a different bug than "undocumented router").
ROUTER_SYMBOL_TO_INVENTORY_ID = {
    "AUMEMMANAGER_ROUTER": "aumemmanager",
    "MEMORY_RETRIEVAL_ROUTER": "memory_retrieval",
    "DATA_GUARDIAN_ROUTER": "data_guardian",
    "INSIGHT_LEDGER_ROUTER": "insight_ledger",
    "QUANTUM_SIMULATOR_ROUTER": "quantum_simulator",
    "rd_router": "rd_pipeline",
    "hr_system_router": "hr_system",
    "collab_router": "cross_repo_collaboration",
    "subroutine_router": "subroutines",
    "subroutine_enhanced_router": "subroutines",
    "EVENT_COORDINATION_ROUTER": "event_coordination",
    "FLEET_BRIDGE_ROUTER": "fleet_bridge",
    "RELAY_MANAGER_ROUTER": "relay_manager",
    "synergy_router": "synergy_api",
    "dashboard_router": "synergy_dashboard",
    "sentinel_router": "resilience_sentinel",
    "monitoring_router": "monitoring_dashboard",
    "gumas_router": "gumas_ethics",
    "auth_router": "oauth2_rbac",
    "r2_telemetry_router": "r2_telemetry",
    "crew_agents_router": "crew_agents",
    "l1_station_router": "l1_station",
    "l2_meta_agent_router": "l2_meta_agents",
    "drift_metrics_router": "drift_metrics",
    "build_sensor_router(_sensor_array)": "sensor_array",
    "qgia_router": "qgia_forecast",
    "checkpoint_vault_router": "checkpoint_vault",
    "playground_router": "playground",
    "cask_router": "cask",
    "token_usage_router": "token_usage_api",
}

# Inventory entries this test doesn't expect an include_router() call for
# (not mounted on api.aurora_api:app — see module docstring).
NOT_MOUNTED_ON_PRIMARY_APP = {
    "primary_fastapi_app",
    "mesh_runtime_v1",
    "pat_terminal_overlay",
    "api_bridge_server",
    "mesh_api_js",
    "enhanced_api_bridge",
    "generated_api_catalog_snapshot",
}


def _inventory_ids() -> set:
    import json

    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    return {e["id"] for e in inventory["entries"]}


def test_every_included_router_has_an_inventory_mapping() -> None:
    """Every app.include_router() call site must resolve to a known
    inventory entry. A router added without updating
    ROUTER_SYMBOL_TO_INVENTORY_ID (and the inventory itself) fails here
    with the exact unmapped symbol named."""
    symbols = extract_include_router_symbols(AURORA_API_PATH.read_text(encoding="utf-8"))
    unmapped = sorted(set(symbols) - set(ROUTER_SYMBOL_TO_INVENTORY_ID))
    assert not unmapped, (
        f"api/aurora_api.py includes router(s) with no entry in "
        f"ROUTER_SYMBOL_TO_INVENTORY_ID (tests/test_api_router_coverage.py): "
        f"{unmapped}. Add an inventory entry in "
        f"docs/api/api_surface_inventory.json and map it here."
    )


def test_every_mapped_router_id_exists_in_inventory() -> None:
    """Every id ROUTER_SYMBOL_TO_INVENTORY_ID points at must actually be
    a live inventory entry — catches a stale mapping (inventory entry
    renamed/removed but this file not updated)."""
    ids = _inventory_ids()
    dangling = sorted(set(ROUTER_SYMBOL_TO_INVENTORY_ID.values()) - ids)
    assert not dangling, (
        f"ROUTER_SYMBOL_TO_INVENTORY_ID references inventory id(s) that no "
        f"longer exist in docs/api/api_surface_inventory.json: {dangling}"
    )


def test_every_main_app_router_inventory_entry_is_actually_included() -> None:
    """Every inventory entry claiming to be a main-app-router must have a
    real include_router() call backing it — catches a stale inventory
    entry (router removed from source but inventory not updated)."""
    import json

    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    main_app_router_ids = {
        e["id"] for e in inventory["entries"]
        if e["service_class"] == "main-app-router" and e["id"] not in NOT_MOUNTED_ON_PRIMARY_APP
    }

    symbols = extract_include_router_symbols(AURORA_API_PATH.read_text(encoding="utf-8"))
    mapped_ids = {ROUTER_SYMBOL_TO_INVENTORY_ID[s] for s in symbols if s in ROUTER_SYMBOL_TO_INVENTORY_ID}

    stale = sorted(main_app_router_ids - mapped_ids)
    assert not stale, (
        f"docs/api/api_surface_inventory.json lists main-app-router "
        f"entries with no corresponding app.include_router() call found "
        f"in api/aurora_api.py: {stale}. Either the router was removed "
        f"(update status/remove the entry) or the mapping in "
        f"tests/test_api_router_coverage.py is stale."
    )


# ── Regression fixtures — synthetic source, not the real repo file ──────
# Prove the extraction logic itself catches an unlisted router and a
# stale inventory entry, independent of api/aurora_api.py's current state.

_SYNTHETIC_SOURCE = """
from fastapi import FastAPI
app = FastAPI()
app.include_router(KNOWN_ROUTER)
app.include_router(build_widget_router(_widget), prefix="/api/widget")
app.include_router(UNLISTED_ROUTER)
"""


def test_regression_extraction_catches_an_unlisted_router() -> None:
    symbols = extract_include_router_symbols(_SYNTHETIC_SOURCE)
    known_mapping = {"KNOWN_ROUTER": "known", "build_widget_router(_widget)": "widget"}
    unmapped = set(symbols) - set(known_mapping)
    assert unmapped == {"UNLISTED_ROUTER"}


def test_regression_extraction_catches_a_stale_inventory_entry() -> None:
    symbols = extract_include_router_symbols(_SYNTHETIC_SOURCE)
    mapping = {"KNOWN_ROUTER": "known", "build_widget_router(_widget)": "widget", "UNLISTED_ROUTER": "unlisted"}
    mapped_ids = {mapping[s] for s in symbols}
    fake_inventory_ids = {"known", "widget", "unlisted", "stale_entry_no_router"}
    stale = fake_inventory_ids - mapped_ids
    assert stale == {"stale_entry_no_router"}
