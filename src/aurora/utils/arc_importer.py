"""Utilities for importing Aurora Recall Chain (ARC) export files.

This module provides a small helper for loading ARC chain exports that are
shared between Aurora CloudBank agents.  The function performs a minimal
validation pass that mirrors the lightweight verification performed when the
bundle is generated and reconstructs the symbolic overlay blocks into an
in-memory thread state dictionary.

The implementation intentionally keeps the structure transparent so that
callers can inspect the reconstructed anchors (T1 metadata, anchor seeds, and
other overlay attributes) without additional transformations.  All validation
errors raise ``ValueError`` to make failure handling explicit for the caller.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping


ARC_EXPORT_SCHEMA = "ARC_CHAIN_EXPORT_SCHEMA_v1.0"


def _ensure_mapping(payload: Mapping[str, Any] | None, error_message: str) -> Mapping[str, Any]:
    """Validate that ``payload`` is a mapping.

    ``ValueError`` is raised with ``error_message`` if validation fails.  This
    helper keeps the main loader readable while still providing targeted error
    messages for diagnostic logs.
    """

    if not isinstance(payload, Mapping):
        raise ValueError(error_message)
    return payload


def import_arc_file(arc_file_path: str | Path) -> Dict[str, Dict[str, Any]]:
    """Load an ARC export and reconstruct the thread state overlays.

    Parameters
    ----------
    arc_file_path:
        Filesystem path to the ARC export JSON file.

    Returns
    -------
    dict[str, dict[str, Any]]
        A mapping keyed by ARC segment type with the associated symbolic
        overlay metadata (summary, timestamp, author, anchor pair).

    Raises
    ------
    FileNotFoundError
        If ``arc_file_path`` does not exist.
    ValueError
        If the file contents do not conform to the ARC export contract.
    json.JSONDecodeError
        If the file is not valid JSON.
    """

    path = Path(arc_file_path)
    if not path.exists():
        raise FileNotFoundError(f"ARC file not found: {path}")

    with path.open("r", encoding="utf-8") as file_handle:
        arc_data = json.load(file_handle)

    schema = arc_data.get("schema")
    if schema != ARC_EXPORT_SCHEMA:
        raise ValueError(f"Unsupported ARC schema '{schema}'. Expected '{ARC_EXPORT_SCHEMA}'.")

    validation_block = _ensure_mapping(
        arc_data.get("validation"),
        "ARC payload missing validation block.",
    )
    if not validation_block.get("validation_passed"):
        raise ValueError("ARC checksum validation failed.")

    arc_chain = arc_data.get("arc_chain")
    if not isinstance(arc_chain, list):
        raise ValueError("ARC chain payload malformed: expected a list of overlay entries.")

    thread_state: Dict[str, Dict[str, Any]] = {}
    required_fields = ("type", "summary", "timestamp", "by", "anchor_pair")
    for entry in arc_chain:
        if not isinstance(entry, dict):
            raise ValueError("ARC chain entry must be an object.")

        missing_fields = [field for field in required_fields if field not in entry]
        if missing_fields:
            raise ValueError(
                f"ARC chain entry missing required fields: {', '.join(sorted(missing_fields))}."
            )

        arc_type = entry["type"]
        thread_state[arc_type] = {
            "summary": entry["summary"],
            "timestamp": entry["timestamp"],
            "by": entry["by"],
            "anchor_pair": entry["anchor_pair"],
        }

    print(f"[RECALL_ARC] Loaded ARC recap: {len(thread_state)} entries.")
    return thread_state


__all__ = ["ARC_EXPORT_SCHEMA", "import_arc_file"]
