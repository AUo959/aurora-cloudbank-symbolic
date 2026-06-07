"""Schema versioning and migration registry for Aurora persisted state files.

Usage:
    registry = MigrationRegistry()
    registry.register("audit_log", 1, migrate_v0_to_v1)

    # When loading a file:
    data = registry.upgrade(data, schema="audit_log")  # upgrades to latest version
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

SCHEMA_VERSION_KEY = "_schema_version"
CURRENT_VERSION = 1  # bump whenever a schema changes

MigrationFn = Callable[[Dict[str, Any]], Dict[str, Any]]


class MigrationRegistry:
    """Registry of schema migrations keyed by (schema_name, from_version)."""

    def __init__(self) -> None:
        # {schema_name: {from_version: migration_fn}}
        self._migrations: Dict[str, Dict[int, MigrationFn]] = {}
        self._latest: Dict[str, int] = {}

    def register(
        self,
        schema: str,
        from_version: int,
        fn: MigrationFn,
        to_version: Optional[int] = None,
    ) -> None:
        """Register a migration from `from_version` to `from_version+1` (or `to_version` if given)."""
        target = to_version if to_version is not None else from_version + 1
        self._migrations.setdefault(schema, {})[from_version] = fn
        self._latest[schema] = max(self._latest.get(schema, 0), target)

    def upgrade(self, data: Dict[str, Any], schema: str) -> Dict[str, Any]:
        """Apply migrations until data is at the latest version for this schema."""
        if not isinstance(data, dict):
            return data
        current = data.get(SCHEMA_VERSION_KEY, 0)
        latest = self._latest.get(schema, CURRENT_VERSION)
        while current < latest:
            fn = self._migrations.get(schema, {}).get(current)
            if fn is None:
                logger.warning(
                    "No migration for %s v%d→v%d, skipping remaining upgrades",
                    schema,
                    current,
                    current + 1,
                )
                break
            try:
                data = fn(data)
                current = data.get(SCHEMA_VERSION_KEY, current + 1)
                logger.info("Migrated %s schema to v%d", schema, current)
            except Exception as exc:
                logger.error("Migration failed for %s v%d: %s", schema, current, exc)
                break
        return data

    def stamp(self, data: Dict[str, Any], schema: str) -> Dict[str, Any]:
        """Add/update the schema version key on a record before writing."""
        data = dict(data)
        data[SCHEMA_VERSION_KEY] = self._latest.get(schema, CURRENT_VERSION)
        return data


# ---------------------------------------------------------------------------
# Process-global default registry
# ---------------------------------------------------------------------------

_default_registry = MigrationRegistry()


def get_registry() -> MigrationRegistry:
    """Return the process-global migration registry."""
    return _default_registry


# ---------------------------------------------------------------------------
# Initial no-op migrations (v0 → v1) for the three core persistence schemas.
# These establish the baseline version so that future structural changes can
# be expressed as v1 → v2 migrations rather than having to handle unversioned
# (v0) records forever.
# ---------------------------------------------------------------------------


def _noop_v0_to_v1(data: Dict[str, Any]) -> Dict[str, Any]:
    """Stamp an unversioned record as v1 without altering any fields."""
    data = dict(data)
    data[SCHEMA_VERSION_KEY] = 1
    return data


# audit_log schema  (src/monitoring/audit_logger.py — JSONL append)
_default_registry.register("audit_log", 0, _noop_v0_to_v1)

# drift_alert schema  (src/monitoring/drift_detector.py — JSONL append)
_default_registry.register("drift_alert", 0, _noop_v0_to_v1)

# monitoring_state schema  (src/monitoring/monitoring_system.py — JSON snapshot)
_default_registry.register("monitoring_state", 0, _noop_v0_to_v1)
