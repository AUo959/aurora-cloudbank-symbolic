"""
Tests for src/runtime/shutdown.py — ShutdownCoordinator (issue #816).
"""

import asyncio
import concurrent.futures
import pytest

from src.runtime.shutdown import ShutdownCoordinator


@pytest.mark.unit
@pytest.mark.asyncio
async def test_registered_task_is_cancelled_on_shutdown():
    """Background tasks registered with the coordinator are cancelled on shutdown."""
    cancelled = asyncio.Event()

    async def long_runner():
        try:
            await asyncio.sleep(9999)
        except asyncio.CancelledError:
            cancelled.set()
            raise

    coordinator = ShutdownCoordinator()
    task = asyncio.create_task(long_runner())
    await asyncio.sleep(0)  # let long_runner reach its first await before cancelling
    coordinator.register(task, name="long_runner")

    await coordinator.shutdown(timeout=2.0)

    assert cancelled.is_set(), "Task should have received CancelledError"
    assert task.cancelled(), "Task should be in cancelled state"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_already_done_task_is_skipped():
    """Tasks that have already completed are not re-cancelled."""
    async def quick():
        return 42

    coordinator = ShutdownCoordinator()
    task = asyncio.create_task(quick())
    await asyncio.sleep(0)  # let it complete
    coordinator.register(task, name="quick")

    # Should not raise
    await coordinator.shutdown(timeout=1.0)
    assert task.done()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_flush_callable_is_invoked_on_shutdown():
    """Flush callables registered with the coordinator are called during shutdown."""
    called = []

    def flush_fn():
        called.append("flushed")

    coordinator = ShutdownCoordinator()
    coordinator.register_flush(flush_fn, name="test flush")
    await coordinator.shutdown(timeout=1.0)

    assert called == ["flushed"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_flush_callable_is_awaited():
    """Async flush callables are properly awaited."""
    called = []

    async def async_flush():
        called.append("async_flushed")

    coordinator = ShutdownCoordinator()
    coordinator.register_flush(async_flush, name="async flush")
    await coordinator.shutdown(timeout=1.0)

    assert called == ["async_flushed"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_flush_exception_does_not_abort_shutdown():
    """A failing flush callable logs a warning but does not stop other flushes."""
    results = []

    def bad_flush():
        raise RuntimeError("flush failed")

    def good_flush():
        results.append("ok")

    coordinator = ShutdownCoordinator()
    coordinator.register_flush(bad_flush, name="bad")
    coordinator.register_flush(good_flush, name="good")

    # Should not raise
    await coordinator.shutdown(timeout=1.0)
    assert results == ["ok"], "Good flush should still run after bad flush"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_executor_is_shut_down():
    """Registered ThreadPoolExecutors are shut down during coordinator shutdown."""
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    work_done = []

    def work():
        work_done.append(True)
        return True

    future = executor.submit(work)
    future.result()  # ensure it completed

    coordinator = ShutdownCoordinator()
    coordinator.register_executor(executor)
    await coordinator.shutdown(timeout=2.0)

    # After shutdown, submitting new work should raise
    with pytest.raises(RuntimeError):
        executor.submit(lambda: None)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_introspection_properties():
    """pending_task_count and registered_flush_count reflect actual state."""
    coordinator = ShutdownCoordinator()

    async def runner():
        await asyncio.sleep(9999)

    task = asyncio.create_task(runner())
    coordinator.register(task, name="t1")
    coordinator.register_flush(lambda: None, name="f1")
    coordinator.register_flush(lambda: None, name="f2")

    assert coordinator.pending_task_count == 1
    assert coordinator.registered_flush_count == 2

    await coordinator.shutdown(timeout=1.0)
    assert coordinator.pending_task_count == 0
