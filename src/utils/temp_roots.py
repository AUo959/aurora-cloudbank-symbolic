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

__all__ = ["TEMP_ROOTS", "resolve_within_temp_root", "is_under_temp_root"]


TEMP_ROOTS: tuple[str, ...] = tuple({
    str(Path(tempfile.gettempdir()).resolve()),
    str(Path(tempfile.gettempdir())),
    str(Path("/tmp").resolve()),  # macOS: /tmp is a symlink to /private/tmp
    "/tmp",
})


def resolve_within_temp_root(path: Path | str) -> Path | None:
    """Resolve *path*; return it only if it genuinely lands inside a temp root.

    Returns ``None`` when the resolved path is outside every temp root.

    **Use the returned path, not the one you passed in.** Callers previously
    validated one value and then used a different one: containment was checked
    against the resolved path (inside the predicate) while the *unresolved* path
    was what got opened.

    In the oldest form of this check — a literal ``startswith("/tmp/")`` on the
    unresolved string — that was directly exploitable: a symlink at
    ``/tmp/innocent.json`` pointing to ``/etc/hosts`` passed the prefix test and
    the caller read the target through it. Resolving inside the predicate closed
    that particular hole, but left a narrower one, because the validated value
    and the used value were still different objects: anything that replaces the
    path with a symlink between the check and the open is followed.

    Returning the resolved path collapses the two into one value, which also
    lets taint analysis see this function as a sanitizer rather than as an
    unchecked path expression.
    """
    resolved = Path(path).resolve()
    resolved_str = str(resolved)
    for root in TEMP_ROOTS:
        if resolved_str == root or resolved_str.startswith(root.rstrip("/") + os.sep):
            return resolved
    return None


def is_under_temp_root(path: Path | str) -> bool:
    """Return True when *path* resolves to somewhere inside a temp directory.

    Prefer :func:`resolve_within_temp_root` at any call site that then opens or
    writes the path — this predicate discards the resolved path, which is what
    makes the check-then-use mismatch described above easy to reintroduce.
    """
    return resolve_within_temp_root(path) is not None
