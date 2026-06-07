"""Tests for src/utils/file_lock — issue #820.

Verifies that DirLock:
  - creates the sentinel file on acquire and removes it on release
  - works as a context manager
  - raises DirLockError when a second instance tries to acquire the same dir
    (two DirLock objects → two distinct open() calls → two file-descriptions;
     fcntl.flock is per open-file-description so the second is blocked)
  - honours AURORA_FORCE_RELEASE_LOCK=1 to clear a stale lock file
  - is safe to release multiple times
  - creates the storage directory if it does not exist
"""
import os
import pytest

from src.utils.file_lock import DirLock, DirLockError, _LOCK_FILENAME, _FORCE_ENV


# ---------------------------------------------------------------------------
# Basic acquire / release
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_acquire_creates_sentinel_file(tmp_path):
    lock = DirLock(tmp_path)
    lock.acquire()
    try:
        assert lock.lock_path.exists(), "Lock sentinel should exist after acquire()"
    finally:
        lock.release()


@pytest.mark.unit
def test_release_removes_sentinel_file(tmp_path):
    lock = DirLock(tmp_path)
    lock.acquire()
    lock.release()
    assert not lock.lock_path.exists(), "Lock sentinel should be removed after release()"


@pytest.mark.unit
def test_lock_path_uses_expected_filename(tmp_path):
    lock = DirLock(tmp_path)
    assert lock.lock_path.name == _LOCK_FILENAME


@pytest.mark.unit
def test_lock_sentinel_contains_pid(tmp_path):
    lock = DirLock(tmp_path)
    lock.acquire()
    try:
        content = lock.lock_path.read_text().strip()
        assert content == str(os.getpid()), "Sentinel should contain current PID"
    finally:
        lock.release()


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_context_manager_acquires_on_enter(tmp_path):
    with DirLock(tmp_path):
        assert (tmp_path / _LOCK_FILENAME).exists()


@pytest.mark.unit
def test_context_manager_releases_on_exit(tmp_path):
    with DirLock(tmp_path):
        pass
    assert not (tmp_path / _LOCK_FILENAME).exists()


@pytest.mark.unit
def test_context_manager_releases_on_exception(tmp_path):
    try:
        with DirLock(tmp_path):
            raise RuntimeError("oops")
    except RuntimeError:
        pass
    assert not (tmp_path / _LOCK_FILENAME).exists()


# ---------------------------------------------------------------------------
# Contention: two DirLock instances on the same directory
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_double_acquire_raises_dir_lock_error(tmp_path):
    """Two DirLock objects on the same dir must contend.

    fcntl.flock locking is per open-file-description (not per-process), so
    two distinct open() calls in the same process DO contend with each other.
    """
    lock1 = DirLock(tmp_path)
    lock1.acquire()
    try:
        lock2 = DirLock(tmp_path)
        with pytest.raises(DirLockError, match="already held"):
            lock2.acquire()
    finally:
        lock1.release()


@pytest.mark.unit
def test_second_acquire_succeeds_after_first_is_released(tmp_path):
    lock1 = DirLock(tmp_path)
    lock1.acquire()
    lock1.release()

    lock2 = DirLock(tmp_path)
    lock2.acquire()  # Should succeed — no one holds the lock
    lock2.release()


# ---------------------------------------------------------------------------
# Force-release via env var
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_force_release_env_var_overrides_stale_lock(tmp_path, monkeypatch):
    """AURORA_FORCE_RELEASE_LOCK=1 should clear a stale lock file."""
    # Simulate a stale lock file left by a crashed process
    stale_pid = "99999"
    (tmp_path / _LOCK_FILENAME).write_text(stale_pid)

    monkeypatch.setenv(_FORCE_ENV, "1")

    lock = DirLock(tmp_path)
    lock.acquire()  # Should succeed after force-clearing the stale file
    try:
        assert lock.lock_path.exists()
        pid_in_file = lock.lock_path.read_text().strip()
        assert pid_in_file == str(os.getpid()), "File should now hold the current PID"
    finally:
        lock.release()


@pytest.mark.unit
def test_force_release_not_set_does_not_clear_lock(tmp_path, monkeypatch):
    """Without AURORA_FORCE_RELEASE_LOCK the second acquire must still fail."""
    monkeypatch.delenv(_FORCE_ENV, raising=False)

    lock1 = DirLock(tmp_path)
    lock1.acquire()
    try:
        lock2 = DirLock(tmp_path)
        with pytest.raises(DirLockError):
            lock2.acquire()
    finally:
        lock1.release()


# ---------------------------------------------------------------------------
# Directory creation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_acquire_creates_nonexistent_directory(tmp_path):
    new_dir = tmp_path / "deep" / "nested" / "dir"
    assert not new_dir.exists()

    lock = DirLock(new_dir)
    lock.acquire()
    try:
        assert new_dir.exists()
        assert lock.lock_path.exists()
    finally:
        lock.release()


# ---------------------------------------------------------------------------
# Idempotent release
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_release_without_acquire_is_safe(tmp_path):
    """Calling release() without prior acquire() should not raise."""
    lock = DirLock(tmp_path)
    lock.release()  # Must not raise


@pytest.mark.unit
def test_double_release_is_safe(tmp_path):
    lock = DirLock(tmp_path)
    lock.acquire()
    lock.release()
    lock.release()  # Second release must not raise
