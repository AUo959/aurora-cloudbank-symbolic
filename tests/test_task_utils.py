"""Tests for src/coordination/task_utils.fire_and_forget."""

import asyncio
import logging

import pytest

from src.coordination.task_utils import fire_and_forget


@pytest.mark.unit
class TestFireAndForget:
    """fire_and_forget() prevents GC cancellation and logs exceptions."""

    def test_task_is_returned(self):
        """fire_and_forget returns the created Task."""
        async def _noop():
            pass

        async def _run():
            task = fire_and_forget(_noop(), name="test-noop")
            assert isinstance(task, asyncio.Task)
            await asyncio.sleep(0)  # yield so task can complete

        asyncio.run(_run())

    def test_task_stored_in_pending_set(self):
        """Task is added to pending_tasks and removed on completion."""
        pending: set = set()

        async def _noop():
            pass

        async def _run():
            fire_and_forget(_noop(), name="test-stored", pending_tasks=pending)
            # Task is in the set immediately after scheduling
            assert len(pending) == 1
            await asyncio.sleep(0)  # let the task finish
            # Task removes itself via done-callback
            assert len(pending) == 0

        asyncio.run(_run())

    def test_exception_logged_not_swallowed(self, caplog):
        """Exceptions inside the coroutine are logged at ERROR level."""

        async def _raises():
            raise RuntimeError("intentional test error")

        async def _run():
            pending: set = set()
            with caplog.at_level(logging.ERROR, logger="src.coordination.task_utils"):
                fire_and_forget(_raises(), name="test-raises", pending_tasks=pending)
                await asyncio.sleep(0.05)

        asyncio.run(_run())

        assert any("intentional test error" in r.message for r in caplog.records), (
            "Expected the exception message to be logged, got: "
            + str([r.message for r in caplog.records])
        )

    def test_cancelled_task_does_not_log_error(self, caplog):
        """A cancelled task is NOT treated as an unhandled exception."""

        async def _long_running():
            await asyncio.sleep(10)

        async def _run():
            pending: set = set()
            with caplog.at_level(logging.ERROR, logger="src.coordination.task_utils"):
                task = fire_and_forget(_long_running(), name="test-cancel", pending_tasks=pending)
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        asyncio.run(_run())

        error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert not error_records, f"Cancellation should not log errors, got: {error_records}"

    def test_fallback_set_used_when_no_pending_tasks(self):
        """Without pending_tasks, the module-level fallback set prevents GC."""
        from src.coordination import task_utils

        async def _noop():
            pass

        async def _run():
            task = fire_and_forget(_noop(), name="test-fallback")
            # The fallback set should contain the task until it finishes
            assert task in task_utils._fallback_tasks
            await asyncio.sleep(0)
            assert task not in task_utils._fallback_tasks

        asyncio.run(_run())
