"""ARC chain import utilities for Aurora CloudBank.

This module focuses on reconstructing thread state overlays from archived
ARC (Aurora Recall Chain) exports. The implementation respects the existing
symbolic metadata conventions by preserving anchor pairs and author
identifiers while ensuring the payload passes integrity validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

SUPPORTED_ARC_SCHEMA = "ARC_CHAIN_EXPORT_SCHEMA_v1.0"


class ArcImportError(RuntimeError):
    """Raised when an ARC chain export cannot be processed."""


def _load_arc_payload(arc_file_path: Path) -> Dict[str, Any]:
    """Load and decode the ARC JSON payload.

    Args:
        arc_file_path: Path to the ARC export file.

    Returns:
        Parsed ARC payload as a dictionary.

    Raises:
        ArcImportError: If the payload cannot be decoded.
    """

    try:
        with arc_file_path.open("r", encoding="utf-8") as arc_file:
            return json.load(arc_file)
    except json.JSONDecodeError as exc:  # pragma: no cover - explicit branch in tests
        raise ArcImportError(f"ARC payload at '{arc_file_path}' is not valid JSON.") from exc


def _validate_arc_payload(payload: Dict[str, Any]) -> None:
    """Validate the ARC payload header and checksum metadata."""

    if payload.get("schema") != SUPPORTED_ARC_SCHEMA:
        raise ArcImportError(
            "Unsupported ARC schema received. "
            f"Expected '{SUPPORTED_ARC_SCHEMA}' but received '{payload.get('schema')}'."
        )

    validation_block = payload.get("validation")
    if not isinstance(validation_block, dict) or not validation_block.get("validation_passed"):
        raise ArcImportError("ARC checksum validation failed.")

    if "arc_chain" not in payload or not isinstance(payload["arc_chain"], list):
        raise ArcImportError("ARC payload is missing the 'arc_chain' sequence.")


def _extract_arc_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and validate a single ARC overlay entry."""

    required_fields = {"type", "summary", "timestamp", "by", "anchor_pair"}
    missing_fields = sorted(required_fields - entry.keys())
    if missing_fields:
        raise ArcImportError("ARC entry missing required fields: " + ", ".join(missing_fields))

    arc_type = entry.get("type")
    if not isinstance(arc_type, str) or not arc_type.strip():
        raise ArcImportError("ARC entry contains an invalid 'type' identifier.")

    return {
        "type": arc_type,
        "summary": entry["summary"],
        "timestamp": entry["timestamp"],
        "by": entry["by"],
        "anchor_pair": entry["anchor_pair"],
    }


def import_arc_file(arc_file_path: str | Path) -> Dict[str, Dict[str, Any]]:
    """Import an ARC chain export and reconstruct the thread state overlays."""

    arc_path = Path(arc_file_path)
    if not arc_path.exists():
        raise FileNotFoundError(f"ARC file '{arc_path}' does not exist.")
    if not arc_path.is_file():
        raise ArcImportError(f"ARC path '{arc_path}' must be a file.")

    payload = _load_arc_payload(arc_path)
    _validate_arc_payload(payload)

    thread_state: Dict[str, Dict[str, Any]] = {}
    for entry in payload.get("arc_chain", []):
        if not isinstance(entry, dict):
            raise ArcImportError("ARC chain entries must be JSON objects.")

        overlay = _extract_arc_entry(entry)
        thread_state[overlay["type"]] = {
            "summary": overlay["summary"],
            "timestamp": overlay["timestamp"],
            "by": overlay["by"],
            "anchor_pair": overlay["anchor_pair"],
        }

    print(f"[RECALL_ARC] Loaded ARC recap: {len(thread_state)} entries.")
    return thread_state
