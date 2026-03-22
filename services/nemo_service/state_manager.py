"""
Aurora NeMo Service — State Manager
# Symbolic Anchor: T1
# SRB: NEMO_SERVICE_v1
# DLP: [nemo, state, snapshot, sha256]
# Chain Notation: #SERVICES//NEMO//STATE_MANAGER//
# Ethics Protocol: Picard_Delta_3
# Anchor Seed: EOS_SEED_ORION

Provides SHA256 hash-sealed simulation state management:

- Create point-in-time snapshots of the NeMo service state
- Verify snapshot integrity via SHA256 checksums
- Restore state from a verified snapshot
- Support time-travel debugging through the snapshot history
"""

import hashlib
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("nemo_service.state_manager")


def _normalise_snapshot_id(snapshot_id: str) -> str:
    """Return a canonical UUID string or raise SnapshotNotFoundError."""
    try:
        return str(uuid.UUID(snapshot_id))
    except (TypeError, ValueError) as exc:
        raise SnapshotNotFoundError(f"Snapshot not found: {snapshot_id}") from exc


def _snapshot_ref(snapshot_id: str) -> str:
    """Return a short log-safe snapshot reference."""
    return snapshot_id[:8]


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class SnapshotNotFoundError(ValueError):
    """Raised when a snapshot ID cannot be located."""


class SnapshotIntegrityError(ValueError):
    """Raised when a snapshot's SHA256 seal does not match its data (tamper detected)."""


# ---------------------------------------------------------------------------
# Snapshot data structure
# ---------------------------------------------------------------------------


@dataclass
class Snapshot:
    """
    A single sealed simulation snapshot.

    The `seal` field is the SHA256 digest of the JSON-serialised `data`
    dict (keys sorted, values converted to strings where not directly
    JSON-serialisable).  Any tampering with `data` will be detected by
    recomputing the seal and comparing it to the stored value.
    """

    snapshot_id: str
    timestamp: float
    data: Dict[str, Any]
    seal: str  # SHA256 hex digest
    anchor_seed: str = "EOS_SEED_ORION"
    srb: str = "NEMO_SERVICE_v1"
    ethics_protocol: str = "Picard_Delta_3"
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dict (safe for JSON encoding)."""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "data": self.data,
            "seal": self.seal,
            "anchor_seed": self.anchor_seed,
            "srb": self.srb,
            "ethics_protocol": self.ethics_protocol,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Snapshot":
        """Deserialise from a plain dict."""
        return cls(
            snapshot_id=d["snapshot_id"],
            timestamp=d["timestamp"],
            data=d["data"],
            seal=d["seal"],
            anchor_seed=d.get("anchor_seed", "EOS_SEED_ORION"),
            srb=d.get("srb", "NEMO_SERVICE_v1"),
            ethics_protocol=d.get("ethics_protocol", "Picard_Delta_3"),
            description=d.get("description", ""),
        )


# ---------------------------------------------------------------------------
# State Manager
# ---------------------------------------------------------------------------


class StateManager:
    """
    SHA256 hash-sealed NeMo simulation state manager.

    All snapshots are stored both in memory (history list) and optionally
    persisted to the `snapshots_dir` as JSON files on disk.  The SHA256
    seal is computed over the JSON-serialised data payload to guarantee
    tamper-detection.

    Usage::

        sm = StateManager(snapshots_dir="/snapshots")
        snapshot_id = sm.create_snapshot(state_data, description="pre-finetune")
        # ... do work ...
        restored = sm.restore_snapshot(snapshot_id)
    """

    def __init__(self, snapshots_dir: str = "/snapshots") -> None:
        """Initialise the state manager with a snapshot storage directory."""
        self._snapshots_dir = snapshots_dir
        self._history: List[Snapshot] = []
        self._current_snapshot_id: Optional[str] = None

        os.makedirs(snapshots_dir, exist_ok=True)
        logger.info(
            "StateManager initialised — snapshots_dir=%s",
            snapshots_dir,
            extra={"chain_notation": "#SERVICES//NEMO//STATE_MANAGER//INIT//"},
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_seal(data: Dict[str, Any]) -> str:
        """
        Compute the SHA256 seal for a data payload.

        Keys are sorted and non-serialisable values are converted to strings
        before hashing so that the seal is deterministic.
        """
        serialised = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialised.encode()).hexdigest()

    def _snapshot_path(self, snapshot_id: str) -> str:
        """Return the on-disk file path for a given snapshot ID."""
        canonical_snapshot_id = _normalise_snapshot_id(snapshot_id)
        return os.path.join(self._snapshots_dir, f"{canonical_snapshot_id}.json")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_snapshot(
        self,
        state_data: Dict[str, Any],
        description: str = "",
        anchor_seed: str = "EOS_SEED_ORION",
    ) -> str:
        """
        Create a new SHA256-sealed snapshot from `state_data`.

        Returns the snapshot ID (UUID4 string).  The snapshot is stored in
        memory and persisted to `snapshots_dir` as a JSON file.

        # Memory sealing: SHA256 hash on all state exports
        """
        snapshot_id = str(uuid.uuid4())
        seal = self._compute_seal(state_data)
        timestamp = time.time()

        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            data=state_data,
            seal=seal,
            anchor_seed=anchor_seed,
            description=description,
        )

        self._history.append(snapshot)
        self._current_snapshot_id = snapshot_id
        self._persist_snapshot(snapshot)

        logger.info(
            "Snapshot created — id=%s seal=%s…",
            snapshot_id,
            seal[:16],
            extra={
                "event": "snapshot_created",
                "snapshot_id": snapshot_id,
                "chain_notation": "#SERVICES//NEMO//SNAPSHOT//CREATE//",
            },
        )

        return snapshot_id

    def verify_snapshot(self, snapshot_id: str) -> bool:
        """
        Verify the SHA256 seal of the named snapshot.

        Returns True if the seal matches the data payload, False if
        tampering is detected.

        # Hash verification: All snapshot operations include SHA256 checksums
        """
        canonical_snapshot_id = _normalise_snapshot_id(snapshot_id)
        snapshot = self._find_snapshot(canonical_snapshot_id)
        if snapshot is None:
            logger.warning("verify_snapshot: snapshot not found — id=%s", _snapshot_ref(canonical_snapshot_id))
            return False

        computed = self._compute_seal(snapshot.data)
        valid = computed == snapshot.seal

        if valid:
            logger.debug("Snapshot verified OK — id=%s", snapshot_id)
        else:
            logger.error(
                "Snapshot seal mismatch — id=%s expected=%s… got=%s…",
                _snapshot_ref(canonical_snapshot_id),
                snapshot.seal[:16],
                computed[:16],
                extra={"event": "snapshot_seal_mismatch"},
            )

        return valid

    def restore_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        Restore and return the data payload from the named snapshot.

        Raises ValueError if the snapshot is not found or if the SHA256 seal
        is invalid (tamper detected).
        """
        canonical_snapshot_id = _normalise_snapshot_id(snapshot_id)
        snapshot = self._find_snapshot(canonical_snapshot_id)
        if snapshot is None:
            raise SnapshotNotFoundError(f"Snapshot not found: {canonical_snapshot_id}")

        if not self.verify_snapshot(canonical_snapshot_id):
            raise SnapshotIntegrityError(f"Snapshot seal verification failed: {canonical_snapshot_id}")

        self._current_snapshot_id = canonical_snapshot_id
        logger.info(
            "Snapshot restored — id=%s seal=%s…",
            _snapshot_ref(canonical_snapshot_id),
            snapshot.seal[:16],
            extra={
                "event": "snapshot_restored",
                "snapshot_id": canonical_snapshot_id,
                "chain_notation": "#SERVICES//NEMO//SNAPSHOT//RESTORE//",
            },
        )

        return snapshot.data

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """Return summary metadata for all stored snapshots (newest first)."""
        snapshots = sorted(self._history, key=lambda s: s.timestamp, reverse=True)
        return [
            {
                "snapshot_id": s.snapshot_id,
                "timestamp": s.timestamp,
                "seal": s.seal,
                "description": s.description,
                "anchor_seed": s.anchor_seed,
            }
            for s in snapshots
        ]

    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Return the full serialised snapshot dict, or None if not found."""
        snapshot = self._find_snapshot(_normalise_snapshot_id(snapshot_id))
        return snapshot.to_dict() if snapshot else None

    def get_current_snapshot_id(self) -> Optional[str]:
        """Return the ID of the most recently created or restored snapshot."""
        return self._current_snapshot_id

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """Look up a snapshot by ID in memory, falling back to disk."""
        canonical_snapshot_id = _normalise_snapshot_id(snapshot_id)
        for s in self._history:
            if s.snapshot_id == canonical_snapshot_id:
                return s

        # Try loading from disk (supports restarts)
        path = self._snapshot_path(canonical_snapshot_id)
        if os.path.isfile(path):
            try:
                with open(path) as fh:
                    data = json.load(fh)
                snapshot = Snapshot.from_dict(data)
                self._history.append(snapshot)
                return snapshot
            except (json.JSONDecodeError, OSError, KeyError, TypeError) as exc:
                logger.error(
                    "Failed to load snapshot from disk — id=%s error=%s",
                    _snapshot_ref(canonical_snapshot_id),
                    exc,
                )

        return None

    def _persist_snapshot(self, snapshot: Snapshot) -> None:
        """Write a snapshot to the snapshots directory as a JSON file."""
        path = self._snapshot_path(snapshot.snapshot_id)
        try:
            with open(path, "w") as fh:
                json.dump(snapshot.to_dict(), fh, indent=2, default=str)
            logger.debug("Snapshot persisted — path=%s", path)
        except OSError as exc:
            logger.warning(
                "Could not persist snapshot to disk — id=%s error=%s",
                snapshot.snapshot_id,
                exc,
            )
