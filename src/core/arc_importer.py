"""Utilities for importing ARC chain export files.

This module provides a focused helper for loading ARC recap bundles that
adhere to the ``ARC_CHAIN_EXPORT_SCHEMA_v1.0`` specification. The importer
performs a light validation pass, reconstructs the symbolic overlay map, and
ensures sensitive fields are redacted before being surfaced to the broader
Aurora stack.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

__all__ = ["ARCImportError", "import_arc_file"]


class ARCImportError(Exception):
    """Raised when an ARC recap bundle cannot be imported safely."""


_PII_EMAIL_PATTERN = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")


def _redact_pii(value: Any) -> Any:
    """Redact simple PII patterns from string fields."""

    if isinstance(value, str):
        return _PII_EMAIL_PATTERN.sub("[REDACTED_EMAIL]", value)
    return value


def _extract_metadata(arc_entry: Dict[str, Any]) -> Dict[str, Any]:
    """Extract metadata fields that should persist on the overlay."""

    metadata: Dict[str, Any] = {}
    for field_name in (
        "metadata",
        "t1_markers",
        "anchor_seeds",
        "symbolic_tags",
        "anchor_traits",
    ):
        if field_name in arc_entry and arc_entry[field_name] is not None:
            metadata[field_name] = arc_entry[field_name]

    return metadata


def import_arc_file(arc_file_path: str | Path) -> Dict[str, Dict[str, Any]]:
    """Import an ARC recap export bundle.

    Parameters
    ----------
    arc_file_path:
        Filesystem path to the ARC JSON export to load.

    Returns
    -------
    Dict[str, Dict[str, Any]]
        A mapping of ARC overlay types to their reconstructed state blocks.

    Raises
    ------
    FileNotFoundError
        If the provided file path does not exist.
    ARCImportError
        If the schema is unsupported, validation fails, or the payload is
        malformed.
    """

    arc_path = Path(arc_file_path)
    if not arc_path.exists():
        raise FileNotFoundError(f"ARC recap file not found: {arc_path}")

    with arc_path.open("r", encoding="utf-8") as arc_file:
        arc_data = json.load(arc_file)

    if arc_data.get("schema") != "ARC_CHAIN_EXPORT_SCHEMA_v1.0":
        raise ARCImportError("Unsupported ARC schema received.")

    validation_block = arc_data.get("validation")
    if not isinstance(validation_block, dict) or not validation_block.get("validation_passed"):
        raise ARCImportError("ARC checksum validation failed.")

    arc_chain = arc_data.get("arc_chain")
    if not isinstance(arc_chain, list):
        raise ARCImportError("ARC chain payload is missing or malformed.")

    thread_state: Dict[str, Dict[str, Any]] = {}
    for arc_entry in arc_chain:
        if not isinstance(arc_entry, dict):
            raise ARCImportError("Encountered malformed ARC entry during import.")

        arc_type = arc_entry.get("type")
        if not arc_type:
            raise ARCImportError("ARC entry missing required 'type' field.")

        overlay_block: Dict[str, Any] = {
            "summary": _redact_pii(arc_entry.get("summary", "")),
            "timestamp": arc_entry.get("timestamp"),
            "by": _redact_pii(arc_entry.get("by", "")),
            "anchor_pair": arc_entry.get("anchor_pair", []),
        }

        metadata = _extract_metadata(arc_entry)
        if metadata:
            overlay_block["metadata"] = metadata

        thread_state[arc_type] = overlay_block

    print(f"[RECALL_ARC] Loaded ARC recap: {len(thread_state)} entries.")
    return thread_state
