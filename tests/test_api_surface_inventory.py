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
        "mesh_runtime_v1",
        "mesh_api_js",
        "enhanced_api_bridge",
    } <= ids
