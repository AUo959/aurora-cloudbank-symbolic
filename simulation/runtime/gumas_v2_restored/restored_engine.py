"""Minimal compatibility restoration of the recovered GUMAS v2.0 combat boundary.

The historical package is imported from the untouched recovery ZIP without
leaving that ZIP at the front of ``sys.path`` or leaving historical
``modules.gumas`` entries installed in ``sys.modules``. Recovered source files
are never rewritten or unpacked into a maintained runtime copy.
"""
from __future__ import annotations

import _imp
import base64
import hashlib
import importlib
import os
import sys
import tempfile
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

RECOVERY_PACKAGE_SHA256 = (
    "039c0f48341aa9847b8400e45a29e41fef734a2b2e80b78bfe3de1abc165ec07"
)
RECOVERY_B64_DIR = Path(__file__).resolve().parent / "vendor" / "recovery_b64"
RESTORATION_VERSION = "2.0.1-restored.2"
RESTORATION_BASE_TREE_SHA256 = (
    "a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9"
)
RESTORATION_CONTRACT = (
    "CombatResolver.resolve_battle(CombatState, attacker_fleets, "
    "defender_fleets, topology_manager)"
)
_HISTORICAL_ROOT = "modules"
_HISTORICAL_PREFIX = "modules.gumas"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _materialize_verified_recovery_zip() -> Path:
    """Reconstruct the historical ZIP atomically and verify it before import."""
    parts = sorted(RECOVERY_B64_DIR.glob("part-*.b64"))
    if not parts:
        raise RuntimeError("GUMAS recovery witness segments are missing")
    encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
    try:
        payload = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise RuntimeError("GUMAS recovery witness base64 is invalid") from exc
    digest = hashlib.sha256(payload).hexdigest()
    if digest != RECOVERY_PACKAGE_SHA256:
        raise RuntimeError(
            f"GUMAS recovery witness hash mismatch: {digest} != {RECOVERY_PACKAGE_SHA256}"
        )

    target = Path(tempfile.gettempdir()) / f"gumas-v2-{digest}.zip"
    if target.exists() and _sha256_file(target) == digest:
        return target

    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent)
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if _sha256_file(temp_path) != digest:
            raise RuntimeError("Materialized GUMAS recovery ZIP failed verification")
        os.replace(temp_path, target)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    if _sha256_file(target) != digest:
        raise RuntimeError("Published GUMAS recovery ZIP failed verification")
    return target


@contextmanager
def _historical_import_scope(recovery_zip: Path) -> Iterator[None]:
    """Temporarily expose historical modules while holding Python's import lock.

    The historical package necessarily uses its original ``modules.gumas``
    package name internally. We therefore expose that namespace only for the
    duration of import, then restore every pre-existing module and path entry.
    The loaded class objects remain referenced locally by this restoration
    module, but future imports resolve against the live repository normally.
    """
    _imp.acquire_lock()
    original_path = list(sys.path)
    saved_modules = {
        name: module
        for name, module in sys.modules.items()
        if name == _HISTORICAL_ROOT
        or name == _HISTORICAL_PREFIX
        or name.startswith(f"{_HISTORICAL_PREFIX}.")
    }
    try:
        for name in list(sys.modules):
            if (
                name == _HISTORICAL_ROOT
                or name == _HISTORICAL_PREFIX
                or name.startswith(f"{_HISTORICAL_PREFIX}.")
            ):
                sys.modules.pop(name, None)
        sys.path.insert(0, str(recovery_zip))
        importlib.invalidate_caches()
        yield
    finally:
        for name in list(sys.modules):
            if (
                name == _HISTORICAL_ROOT
                or name == _HISTORICAL_PREFIX
                or name.startswith(f"{_HISTORICAL_PREFIX}.")
            ):
                sys.modules.pop(name, None)
        sys.modules.update(saved_modules)
        sys.path[:] = original_path
        importlib.invalidate_caches()
        _imp.release_lock()


RECOVERY_ZIP = _materialize_verified_recovery_zip()
with _historical_import_scope(RECOVERY_ZIP):
    from modules.gumas.engine import GUMASEngine as HistoricalGUMASEngine
    from modules.gumas.models import (
        BattlefieldCondition,
        CombatState,
        EventType,
        FleetState,
        GUMASState,
        SimulationEvent,
        TickResult,
    )


class GUMASEngine(HistoricalGUMASEngine):
    """Recovered v2.0 engine with the smallest coherent combat-call restoration."""

    def _battlefield_condition_for_location(
        self, location: str
    ) -> BattlefieldCondition:
        """Resolve an aggregate battlefield condition deterministically."""
        if self._topology_manager and self._state.topology:
            node = self._state.topology.nodes.get(location)
            if node and node.is_chokepoint:
                return BattlefieldCondition.CHOKEPOINT
        return BattlefieldCondition.OPEN_SPACE

    @staticmethod
    def _combat_id(location: str, fid_a: str, fid_b: str) -> str:
        """Return a stable combat identifier for one faction pair at one location."""
        first, second = sorted((fid_a, fid_b))
        return f"combat::{location}::{first}::{second}"

    def _prepare_combat_state(
        self,
        location: str,
        fid_a: str,
        fleets_a: List[FleetState],
        fid_b: str,
        fleets_b: List[FleetState],
        condition: Optional[BattlefieldCondition] = None,
    ) -> CombatState:
        """Create or update the CombatState required by the shipped resolver."""
        combat_id = self._combat_id(location, fid_a, fid_b)
        combat = self._state.combat_zones.get(combat_id)
        if combat is None:
            combat = CombatState(
                combat_id=combat_id,
                location=location,
                attacker_fleets=sorted(f.fleet_id for f in fleets_a),
                defender_fleets=sorted(f.fleet_id for f in fleets_b),
                condition=condition
                or self._battlefield_condition_for_location(location),
            )
            self._state.combat_zones[combat_id] = combat
        else:
            combat.attacker_fleets = sorted(f.fleet_id for f in fleets_a)
            combat.defender_fleets = sorted(f.fleet_id for f in fleets_b)
            if condition is not None:
                combat.condition = condition
        return combat

    def _resolve_fleet_pair(
        self,
        location: str,
        fid_a: str,
        fleets_a: List[FleetState],
        fid_b: str,
        fleets_b: List[FleetState],
    ) -> Dict[str, Any]:
        """Resolve one aggregate engagement through the shipped v2 resolver contract."""
        fleets_a = sorted(fleets_a, key=lambda fleet: fleet.fleet_id)
        fleets_b = sorted(fleets_b, key=lambda fleet: fleet.fleet_id)
        combat = self._prepare_combat_state(
            location, fid_a, fleets_a, fid_b, fleets_b
        )
        outcome = self._combat_resolver.resolve_battle(
            combat=combat,
            attacker_fleets=fleets_a,
            defender_fleets=fleets_b,
            topology_manager=self._topology_manager,
        )
        self._combat_resolver.apply_fleet_losses(
            fleets_a, outcome.get("attacker_losses", 0)
        )
        self._combat_resolver.apply_fleet_losses(
            fleets_b, outcome.get("defender_losses", 0)
        )
        combat.outcome_ratio = outcome.get("outcome_ratio", 1.0)
        combat.turns_active += 1
        return outcome

    def _combat_resolution_tick(self, result: TickResult) -> None:
        """Resolve one deterministic aggregate engagement per faction pair/location."""
        location_fleets = defaultdict(lambda: defaultdict(list))
        for fleet in self._state.fleets.values():
            location_fleets[fleet.location_node][fleet.faction_id].append(fleet)

        for location in sorted(location_fleets):
            fleets_by_faction = location_fleets[location]
            if len(fleets_by_faction) <= 1:
                continue
            faction_ids = sorted(fleets_by_faction)
            for i, fid_a in enumerate(faction_ids):
                for fid_b in faction_ids[i + 1 :]:
                    outcome = self._resolve_fleet_pair(
                        location,
                        fid_a,
                        fleets_by_faction[fid_a],
                        fid_b,
                        fleets_by_faction[fid_b],
                    )
                    self._append_state_change(
                        result,
                        f"combat[{fid_a}-{fid_b}] at {location} "
                        f"winner={outcome.get('winner')}",
                    )

    def _handle_fleet_battle(
        self, event: SimulationEvent, result: TickResult
    ) -> None:
        """Prepare explicit battle context; Phase 9 performs the single resolution."""
        location = event.parameters.get("location")
        if not location:
            return

        fleets_at_location = defaultdict(list)
        for fleet in self._state.fleets.values():
            if fleet.location_node == location:
                fleets_at_location[fleet.faction_id].append(fleet)

        if len(fleets_at_location) < 2:
            return

        condition = None
        raw_condition = event.parameters.get("condition")
        if raw_condition is not None:
            condition = (
                raw_condition
                if isinstance(raw_condition, BattlefieldCondition)
                else BattlefieldCondition(raw_condition)
            )

        faction_ids = sorted(fleets_at_location)
        for i, fid_a in enumerate(faction_ids):
            for fid_b in faction_ids[i + 1 :]:
                self._prepare_combat_state(
                    location,
                    fid_a,
                    sorted(
                        fleets_at_location[fid_a],
                        key=lambda fleet: fleet.fleet_id,
                    ),
                    fid_b,
                    sorted(
                        fleets_at_location[fid_b],
                        key=lambda fleet: fleet.fleet_id,
                    ),
                    condition=condition,
                )
                self._append_state_change(
                    result,
                    f"fleet_battle_prepared[{fid_a}-{fid_b}] at {location}",
                )
