"""
Atomic I/O helpers for safe file writes.

Provides atomic JSON write operations that prevent partial/corrupt files
by writing to a temporary file first, then atomically renaming it.
"""

import json
import os
import tempfile
import logging
from typing import Any

logger = logging.getLogger(__name__)


def atomic_write_json(path: str, data: Any, indent: int = 2) -> None:
    """Write *data* to *path* as JSON atomically.

    The write is performed to a sibling temp file in the same directory and
    then renamed over *path*.  This guarantees that readers never see a
    partially-written file, even if the process is interrupted mid-write.

    Args:
        path:   Destination file path (will be created or overwritten).
        data:   JSON-serialisable Python object.
        indent: Pretty-print indentation level (default 2).

    Raises:
        TypeError: If *data* is not JSON-serialisable.
        OSError:   If the destination directory is not writable.
    """
    dest_dir = os.path.dirname(os.path.abspath(path))
    os.makedirs(dest_dir, exist_ok=True)

    # Write to a temp file in the same directory so that os.replace() is
    # guaranteed to be atomic (same filesystem).
    fd, tmp_path = tempfile.mkstemp(dir=dest_dir, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=indent, default=str)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, path)
    except Exception:
        # Clean up the temp file if anything goes wrong.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
