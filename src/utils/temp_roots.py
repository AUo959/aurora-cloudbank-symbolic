"""Platform-correct detection of the system temporary directory.

Several path-validation sites need to answer "is this path inside a temp
directory?" — usually to let a test suite hand fixture paths to code that
otherwise refuses absolute paths.

Every one of them originally spelled that check ``str(path).startswith("/tmp/")``,
which is a Linux-only assumption and silently wrong elsewhere:

* On macOS ``tempfile.gettempdir()`` returns ``/var/folders/<...>/T/`` — nothing
  a ``/tmp/`` prefix test will ever match, so ``pytest``'s ``tmp_path`` fixtures
  were rejected outright.
* Also on macOS ``/tmp`` is a symlink to ``/private/tmp``, so ``Path.resolve()``
  returns a string that the literal ``"/tmp/"`` prefix does not match either.
* Anywhere ``TMPDIR`` is set to a non-default location, the check misses.

``_TEMP_ROOTS`` therefore collects the temp directory both as reported and as
resolved, plus ``/tmp`` in both forms, and comparison is done on a resolved
path with an ``os.sep`` boundary so ``/tmpfoo`` is not mistaken for ``/tmp/foo``.

Security note: this module answers *only* "is this under a temp root". It is a
location test, not an authorization decision. Temp directories are typically
world-writable and symlink-farmable, so callers that use a positive result to
waive a containment check are widening their trust boundary — see
``modules/insight_ledger/ledger_core.validate_safe_path`` for one that does.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

__all__ = ["TEMP_ROOTS", "is_under_temp_root"]


TEMP_ROOTS: tuple[str, ...] = tuple({
    str(Path(tempfile.gettempdir()).resolve()),
    str(Path(tempfile.gettempdir())),
    str(Path("/tmp").resolve()),  # macOS: /tmp is a symlink to /private/tmp
    "/tmp",
})


def is_under_temp_root(path: Path | str) -> bool:
    """Return True when *path* sits inside a platform temp directory.

    The path is resolved before comparison, so a symlink pointing into a temp
    directory counts as being inside one.
    """
    resolved = str(Path(path).resolve())
    return any(
        resolved == root or resolved.startswith(root.rstrip("/") + os.sep)
        for root in TEMP_ROOTS
    )
