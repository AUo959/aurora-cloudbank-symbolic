"""Instance-level advisory file locks to prevent two processes sharing a state dir.

Uses ``fcntl.flock`` on POSIX (Linux/macOS) with a best-effort PID-file fallback
on Windows (where ``fcntl`` is not available).  The lock sentinel is a hidden file
``<storage_dir>/.aurora.lock`` that contains the owning process's PID.

Usage (explicit acquire/release)::

    lock = DirLock(storage_dir)
    lock.acquire()          # raises DirLockError if already held
    try:
        # ... exclusive access ...
    finally:
        lock.release()

Usage (context manager, preferred)::

    with DirLock(storage_dir):
        # exclusive access guaranteed

Emergency override::

    Set the environment variable ``AURORA_FORCE_RELEASE_LOCK=1`` to forcibly
    remove a stale lock file before attempting to acquire.  Use only when you
    are certain the previous holder has crashed.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import IO, Optional

logger = logging.getLogger(__name__)

_LOCK_FILENAME: str = ".aurora.lock"
_FORCE_ENV: str = "AURORA_FORCE_RELEASE_LOCK"


class DirLockError(RuntimeError):
    """Raised when a directory lock cannot be acquired."""


class DirLock:
    """Advisory exclusive lock on a storage directory.

    Args:
        storage_dir: Path to the directory that should be exclusively owned.
    """

    def __init__(self, storage_dir: "Path | str") -> None:
        self._dir: Path = Path(storage_dir)
        self._fh: Optional[IO[str]] = None
        self._pid_file_path: Optional[Path] = None  # Windows fallback sentinel

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def lock_path(self) -> Path:
        """Full path to the sentinel lock file."""
        return self._dir / _LOCK_FILENAME

    def acquire(self) -> None:
        """Acquire exclusive lock on the storage directory.

        Raises:
            DirLockError: If the lock is already held by another process.
        """
        force = os.getenv(_FORCE_ENV, "").strip() == "1"
        if force:
            logger.warning(
                "%s=1 — forcibly releasing existing lock on %s",
                _FORCE_ENV,
                self._dir,
            )
            try:
                self.lock_path.unlink(missing_ok=True)
            except Exception:
                pass

        self._dir.mkdir(parents=True, exist_ok=True)

        try:
            import fcntl  # noqa: PLC0415  (POSIX-only)
            self._fh = open(self.lock_path, "w")  # noqa: WPS515 — intentional keep-open
            self._fh.write(str(os.getpid()))
            self._fh.flush()
            fcntl.flock(self._fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.debug("Acquired dir lock: %s (pid=%d)", self._dir, os.getpid())
        except ImportError:
            # Windows — fcntl unavailable; use best-effort PID file
            self._acquire_pid_file()
        except OSError as exc:
            if self._fh is not None:
                self._fh.close()
                self._fh = None
            pid_hint = self._read_lock_pid()
            raise DirLockError(
                f"Cannot acquire lock on {self._dir} — already held by pid {pid_hint}. "
                f"If the holder crashed, set {_FORCE_ENV}=1 to override."
            ) from exc

    def release(self) -> None:
        """Release the lock and remove the sentinel file.

        Safe to call even if the lock was never successfully acquired.
        """
        # POSIX path: unlock via fcntl then close the file handle
        if self._fh is not None:
            try:
                import fcntl
                fcntl.flock(self._fh, fcntl.LOCK_UN)
            except Exception:
                pass
            try:
                self._fh.close()
            except Exception:
                pass
            self._fh = None

        # Remove the lock sentinel
        try:
            self.lock_path.unlink(missing_ok=True)
        except Exception:
            pass

        # Windows path: remove the PID file sentinel
        if self._pid_file_path is not None:
            try:
                self._pid_file_path.unlink(missing_ok=True)
            except Exception:
                pass
            self._pid_file_path = None

        logger.debug("Released dir lock: %s", self._dir)

    # ------------------------------------------------------------------
    # Context-manager protocol
    # ------------------------------------------------------------------

    def __enter__(self) -> "DirLock":
        self.acquire()
        return self

    def __exit__(self, *_args: object) -> None:
        self.release()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _acquire_pid_file(self) -> None:
        """Windows fallback: best-effort PID file (not atomic)."""
        if self.lock_path.exists():
            pid_hint = self._read_lock_pid()
            raise DirLockError(
                f"Lock file exists at {self.lock_path} (pid={pid_hint}). "
                f"Set {_FORCE_ENV}=1 to override."
            )
        self._pid_file_path = self.lock_path
        self._pid_file_path.write_text(str(os.getpid()))
        logger.debug("Acquired dir lock (pid-file): %s (pid=%d)", self._dir, os.getpid())

    def _read_lock_pid(self) -> str:
        """Read the PID stored in the lock file, or return 'unknown'."""
        try:
            return self.lock_path.read_text().strip()
        except Exception:
            return "unknown"
