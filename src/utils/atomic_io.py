"""Crash-safe file I/O helpers (#807).

Background: Aurora's state-bearing modules previously wrote with
``open(path, "w")`` and appended without ``fsync``. A SIGKILL,
container OOM-kill, or power loss mid-write left half-written files
that either failed to parse on restart or silently truncated state.

This module centralises two patterns:

  * ``atomic_write_text(path, text)`` -- write the new contents to a
    sibling ``.tmp`` file, fsync the tmp file, then ``os.replace`` it
    over the destination. ``os.replace`` is atomic on POSIX (rename(2)
    semantics) and on Windows, so a crash before ``replace`` leaves the
    original intact; a crash after leaves the new contents intact.

  * ``append_jsonl(path, record)`` -- open the destination in append
    mode, write one JSON-serialised line, then fsync the file
    descriptor. A crash mid-write may still tear the last line; the
    fsync guarantees that everything BEFORE the in-flight write is
    durable, which is the strongest guarantee a single append-only
    file can give without rotating files.

These helpers intentionally do nothing fancy: no compression, no
encryption, no rotation. They are crash-safety primitives. Anything
richer belongs in a dedicated store.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def atomic_write_text(path: str | os.PathLike[str], text: str) -> None:
    """Replace ``path`` with ``text`` atomically.

    The parent directory must exist. If it doesn't, callers should
    ``mkdir(parents=True, exist_ok=True)`` first -- this helper does not
    create directories so that misconfigured paths fail loudly instead
    of silently mushrooming directory trees.
    """
    dest = Path(path)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, dest)


def atomic_write_json(path: str | os.PathLike[str], payload: Any, *, indent: int | None = 2) -> None:
    """Convenience: JSON-serialise then atomic_write_text."""
    atomic_write_text(path, json.dumps(payload, indent=indent, default=str))


def append_jsonl(path: str | os.PathLike[str], record: Any) -> None:
    """Append ``record`` as a single JSONL line and fsync.

    ``record`` is serialised with ``json.dumps(..., default=str)`` so
    datetimes / Paths flow through without special-casing.
    """
    line = json.dumps(record, default=str) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())
