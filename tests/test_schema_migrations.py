"""Tests for src/utils/schema_migrations.py

Covers:
- Registry with no migrations registered
- Single v0→v1 migration applied
- Chained migrations (v0→v1→v2)
- Missing intermediate migration: logs warning and stops
- stamp() adds _schema_version key
- Non-dict data returned unchanged by upgrade()
- Data already at latest version is returned unchanged
- to_version parameter in register()
- Default registry / get_registry()
- Stamp reflects latest registered version for schema
"""

import logging
import pytest

from src.utils.schema_migrations import (
    MigrationRegistry,
    SCHEMA_VERSION_KEY,
    CURRENT_VERSION,
    get_registry,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _add_v(data, version):
    """Return a copy of data with _schema_version set."""
    return {**data, SCHEMA_VERSION_KEY: version}


# ---------------------------------------------------------------------------
# Tests: upgrade()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_upgrade_no_migrations_returns_data_unchanged():
    """Registry with no migrations: upgrade returns data unchanged."""
    registry = MigrationRegistry()
    data = {"foo": "bar"}
    result = registry.upgrade(data, schema="nonexistent")
    # Data should be returned as-is; no _schema_version injected
    assert result["foo"] == "bar"


@pytest.mark.unit
def test_upgrade_single_migration_v0_to_v1():
    """Single registered migration transforms data from v0 to v1."""
    registry = MigrationRegistry()

    def migrate(d):
        d = dict(d)
        d["migrated"] = True
        d[SCHEMA_VERSION_KEY] = 1
        return d

    registry.register("test_schema", 0, migrate)
    data = {"value": 42}  # no _schema_version → treated as v0
    result = registry.upgrade(data, schema="test_schema")

    assert result[SCHEMA_VERSION_KEY] == 1
    assert result["migrated"] is True
    assert result["value"] == 42


@pytest.mark.unit
def test_upgrade_chain_v0_to_v1_to_v2():
    """Chain of two migrations applied in order: v0→v1→v2."""
    registry = MigrationRegistry()

    def v0_to_v1(d):
        d = dict(d)
        d["step1"] = True
        d[SCHEMA_VERSION_KEY] = 1
        return d

    def v1_to_v2(d):
        d = dict(d)
        d["step2"] = True
        d[SCHEMA_VERSION_KEY] = 2
        return d

    registry.register("chain_schema", 0, v0_to_v1)
    registry.register("chain_schema", 1, v1_to_v2)

    data = {"original": True}
    result = registry.upgrade(data, schema="chain_schema")

    assert result[SCHEMA_VERSION_KEY] == 2
    assert result["step1"] is True
    assert result["step2"] is True
    assert result["original"] is True


@pytest.mark.unit
def test_upgrade_missing_intermediate_stops_and_warns(caplog):
    """Missing intermediate migration logs a warning and stops upgrading."""
    registry = MigrationRegistry()

    # Only register v1→v2; leave v0→v1 missing so the loop can't start
    def v1_to_v2(d):
        d = dict(d)
        d[SCHEMA_VERSION_KEY] = 2
        return d

    # Manually set latest to 2 by registering v1 migration with to_version=2
    registry.register("gap_schema", 1, v1_to_v2, to_version=2)

    # Data at v0 — the registry has no v0 migration
    data = {"payload": "x"}  # v0 (no _schema_version key)

    with caplog.at_level(logging.WARNING, logger="src.utils.schema_migrations"):
        result = registry.upgrade(data, schema="gap_schema")

    # Should stop at v0 because no migration found
    assert result.get(SCHEMA_VERSION_KEY, 0) == 0
    assert any("No migration" in record.message for record in caplog.records)


@pytest.mark.unit
def test_upgrade_already_at_latest_returns_unchanged():
    """Data already at the latest version is returned without modification."""
    registry = MigrationRegistry()
    call_count = {"n": 0}

    def v0_to_v1(d):
        call_count["n"] += 1
        d = dict(d)
        d[SCHEMA_VERSION_KEY] = 1
        return d

    registry.register("stamped_schema", 0, v0_to_v1)

    data = {"already": True, SCHEMA_VERSION_KEY: 1}
    result = registry.upgrade(data, schema="stamped_schema")

    assert result[SCHEMA_VERSION_KEY] == 1
    assert call_count["n"] == 0  # migration was never called


@pytest.mark.unit
def test_upgrade_non_dict_returned_unchanged():
    """Non-dict values passed to upgrade() are returned as-is."""
    registry = MigrationRegistry()
    registry.register("any_schema", 0, lambda d: d)

    for value in [None, "string", 42, [1, 2, 3]]:
        assert registry.upgrade(value, schema="any_schema") is value


# ---------------------------------------------------------------------------
# Tests: stamp()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_stamp_adds_schema_version_key():
    """stamp() adds _schema_version to the returned dict."""
    registry = MigrationRegistry()
    registry.register("my_schema", 0, lambda d: d)

    record = {"event": "login"}
    stamped = registry.stamp(record, schema="my_schema")

    assert SCHEMA_VERSION_KEY in stamped
    assert stamped[SCHEMA_VERSION_KEY] == 1


@pytest.mark.unit
def test_stamp_does_not_mutate_original():
    """stamp() returns a new dict and does not mutate the input."""
    registry = MigrationRegistry()
    registry.register("immutable_schema", 0, lambda d: d)

    original = {"data": "value"}
    stamped = registry.stamp(original, schema="immutable_schema")

    assert SCHEMA_VERSION_KEY not in original
    assert SCHEMA_VERSION_KEY in stamped


@pytest.mark.unit
def test_stamp_reflects_latest_registered_version():
    """stamp() uses the latest known version for the schema."""
    registry = MigrationRegistry()

    def noop(d):
        d = dict(d)
        d[SCHEMA_VERSION_KEY] = 3
        return d

    registry.register("versioned_schema", 2, noop, to_version=3)
    stamped = registry.stamp({"x": 1}, schema="versioned_schema")
    assert stamped[SCHEMA_VERSION_KEY] == 3


@pytest.mark.unit
def test_stamp_unknown_schema_uses_current_version():
    """stamp() falls back to CURRENT_VERSION for unregistered schemas."""
    registry = MigrationRegistry()
    stamped = registry.stamp({"y": 2}, schema="unknown_schema")
    assert stamped[SCHEMA_VERSION_KEY] == CURRENT_VERSION


# ---------------------------------------------------------------------------
# Tests: default registry / get_registry()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_registry_returns_migration_registry_instance():
    """get_registry() returns a MigrationRegistry."""
    registry = get_registry()
    assert isinstance(registry, MigrationRegistry)


@pytest.mark.unit
def test_default_registry_stamps_audit_log():
    """Default registry can stamp an audit_log record."""
    registry = get_registry()
    record = {"id": "AUDIT-00000001", "event_type": "drift_alert"}
    stamped = registry.stamp(record, schema="audit_log")
    assert stamped[SCHEMA_VERSION_KEY] == 1


@pytest.mark.unit
def test_default_registry_upgrades_unversioned_drift_alert():
    """Default registry upgrades an unversioned drift_alert record to v1."""
    registry = get_registry()
    old_record = {"agent_id": "agent-001", "level": "warning"}
    upgraded = registry.upgrade(old_record, schema="drift_alert")
    assert upgraded[SCHEMA_VERSION_KEY] == 1
    assert upgraded["agent_id"] == "agent-001"


@pytest.mark.unit
def test_default_registry_upgrades_unversioned_monitoring_state():
    """Default registry upgrades an unversioned monitoring_state record to v1."""
    registry = get_registry()
    old_state = {"interventions": [], "last_intervention_time": {}}
    upgraded = registry.upgrade(old_state, schema="monitoring_state")
    assert upgraded[SCHEMA_VERSION_KEY] == 1
