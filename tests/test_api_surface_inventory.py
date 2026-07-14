"""Structural checks for the governed API inventory.

These tests validate schema and named regression contracts. They do not prove
complete coverage of routers mounted by the live applications; see issue #1204.
"""

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = REPO_ROOT / "docs" / "api" / "api_surface_inventory.json"


def test_api_surface_inventory_is_valid() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

    allowed_statuses = set(inventory["status_values"])
    assert inventory["governance_decision"] == "primary-fastapi-with-declared-standalone-services"
    assert inventory["entries"]

    required_fields = {
        "id",
        "owner",
        "runtime",
        "entrypoint",
        "mount_path",
        "service_class",
        "status",
        "status_evidence",
        "notes",
    }

    seen_ids = set()
    for entry in inventory["entries"]:
        assert required_fields <= set(entry), entry
        assert entry["id"] not in seen_ids
        seen_ids.add(entry["id"])
        assert entry["status"] in allowed_statuses
        assert entry["status_evidence"]

        if entry["mount_path"] != "n/a":
            assert entry["mount_path"].startswith(("/", ":")), entry

        path = REPO_ROOT / entry["entrypoint"]
        assert path.exists(), entry


def test_required_api_surface_entries_are_present() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    ids = {entry["id"] for entry in inventory["entries"]}

    assert {
        "primary_fastapi_app",
        "hr_system",
        "monitoring_dashboard",
        "drift_metrics",
        "gumas_ethics",
        "l1_station",
        "sensor_array",
        "checkpoint_vault",
        "cask",
        "mesh_runtime_v1",
        "pat_terminal_overlay",
        "qgia_forecast",
        "mesh_api_js",
        "enhanced_api_bridge",
    } <= ids


def test_reconciled_mesh_qgia_pat_and_consent_contracts() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    entries = {entry["id"]: entry for entry in inventory["entries"]}

    mesh_mounts = entries["mesh_runtime_v1"]["mount_path"]
    assert "/api/mesh/agents" in mesh_mounts
    assert "/api/mesh/agents/{agent_id}" in mesh_mounts
    assert "/api/mesh/agents/{agent_id}/activate" in mesh_mounts

    assert entries["qgia_forecast"]["mount_path"] == "/qgia"
    assert "not the generic L1 inter-node exchange transport" in entries["qgia_forecast"]["notes"]

    pat = entries["pat_terminal_overlay"]
    assert pat["status"] == "active-standalone"
    assert "/api/mesh/terminals" in pat["mount_path"]
    assert "Read-only Personal Access Terminal" in pat["notes"]

    rd_notes = entries["rd_pipeline"]["notes"]
    assert "implemented at /rd/consent" in rd_notes
    assert "#1200" in rd_notes

    consent = entries["rd_consent"]
    assert consent["mount_path"] == "/rd/consent"
    assert consent["entrypoint"] == "modules/hr/consent/api.py"
    assert "insight_ledger" in consent["notes"]


def test_governance_review_router_dispositions() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    entries = {entry["id"]: entry for entry in inventory["entries"]}

    assert entries["l1_station"]["mount_path"] == "/api/aurora"
    assert entries["sensor_array"]["mount_path"] == "/api/sensors"
    assert entries["checkpoint_vault"]["mount_path"] == "/checkpoint"
    assert entries["cask"]["mount_path"] == "/api/cask"

    for entry_id in ("l1_station", "sensor_array", "checkpoint_vault", "cask"):
        assert entries[entry_id]["status"] == "active"
        assert entries[entry_id]["service_class"] == "main-app-router"
