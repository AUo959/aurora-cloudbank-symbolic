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

``TEMP_ROOTS`` therefore collects the temp directory both as reported and as
resolved, plus ``/tmp`` in both forms. Compare a **resolved** path against it
with an ``os.sep`` boundary, so ``/tmpfoo`` is not mistaken for ``/tmp/foo``.

Why this module exports data rather than a predicate that call sites use to
guard filesystem access
-----------------------------------------------------------------------------
CodeQL's ``py/path-injection`` query follows a caller-controlled path from its
source to the filesystem call that consumes it, and it recognises a containment
check as a sanitizer only when the check and the use are in the same function.
Routing the check through a helper that returns a ``bool`` — or an
``Optional[Path]`` — hides it from that analysis, and the call site is then
reported as an unguarded path expression. Extracting the helper here is what
introduced two high-severity alerts on a branch whose base had none.

So each call site that goes on to touch the filesystem spells the comparison out
next to the use it protects, via :func:`is_within_temp_root` used inline, and
this module owns the platform data plus this explanation. That costs a couple of
duplicated lines and keeps the guard visible to both readers and analysis.

Security note: this answers *only* "is this under a temp root". It is a location
test, not an authorization decision. Temp directories are typically
world-writable and symlink-farmable, so a caller that treats a positive result
as licence to skip its own containment check is widening its trust boundary —
see ``modules/insight_ledger/ledger_core.validate_safe_path``, which does
exactly that so the ledger's test-suite can hand it absolute fixture paths.

Always compare the **resolved** path and then use *that same* resolved value.
Checking one object and opening another is how the original
``startswith("/tmp/")`` form let a symlink at ``/tmp/innocent.json`` pointing at
``/etc/hosts`` pass the check and be read through on open.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

__all__ = ["TEMP_ROOTS", "is_within_temp_root", "is_under_temp_root"]


TEMP_ROOTS: tuple[str, ...] = tuple({
    str(Path(tempfile.gettempdir()).resolve()),
    str(Path(tempfile.gettempdir())),
    str(Path("/tmp").resolve()),  # macOS: /tmp is a symlink to /private/tmp
    "/tmp",
})


def is_within_temp_root(resolved: Path) -> bool:
    """True when *resolved* — which must already be resolved — is under a temp root.

    Takes an already-resolved path on purpose. Resolving internally would let a
    caller pass an unresolved path, get True, and then use the unresolved value,
    which is the check-then-use mismatch described in the module docstring.
    """
    resolved_str = str(resolved)
    return any(
        resolved_str == root or resolved_str.startswith(root.rstrip("/") + os.sep)
        for root in TEMP_ROOTS
    )


def is_under_temp_root(path: Path | str) -> bool:
    """Resolve *path* and report whether it lands inside a temp directory.

    For callers that only need the location answer and do **not** go on to open
    or write the path. Anything that does touch the filesystem should resolve
    once itself and guard with :func:`is_within_temp_root` inline, so the check
    and the use stay in one function — see the module docstring.
    """
    return is_within_temp_root(Path(path).resolve())
