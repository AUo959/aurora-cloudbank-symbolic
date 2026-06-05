"""
Shutdown Coordinator
=====================
Centralises graceful-shutdown logic for the Aurora API process.

Usage (in lifespan):

    coordinator = ShutdownCoordinator()

    # During startup, register anything that needs cleanup:
    bg_task = asyncio.create_task(my_background_loop())
    coordinator.register(bg_task, name="my_background_loop")

    coordinator.register_executor(thread_pool)

    coordinator.register_flush(monitoring_system.export_state)

    yield  # serve requests

    # On shutdown:
    await coordinator.shutdown(timeout=10.0)
"""

import asyncio
import concurrent.futures
import logging
from typing import Any, Callable, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ShutdownCoordinator:
    """
    Coordinates graceful shutdown of background tasks, thread-pool executors,
    and async/sync flush callables.

    Registration order matters: tasks are cancelled in reverse order so
    higher-level dependents are stopped before lower-level producers.
    """

    def __init__(self) -> None:
        self._tasks: List[Tuple[asyncio.Task, str]] = []
        self._executors: List[concurrent.futures.Executor] = []
        self._flushes: List[Tuple[Callable[[], Any], str]] = []

    # ------------------------------------------------------------------
    # Registration API
    # ------------------------------------------------------------------

    def register(self, task: "asyncio.Task[Any]", name: str = "") -> None:
        """Register a background asyncio Task for cancellation on shutdown."""
        self._tasks.append((task, name or repr(task)))

    def register_executor(self, executor: concurrent.futures.Executor, name: str = "") -> None:
        """Register a ThreadPoolExecutor (or any Executor) for orderly shutdown."""
        self._executors.append(executor)

    def register_flush(self, fn: Callable[[], Any], name: str = "") -> None:
        """Register a zero-argument callable (sync or async) to run before exit."""
        self._flushes.append((fn, name or getattr(fn, "__name__", repr(fn))))

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    async def shutdown(self, timeout: float = 10.0) -> None:
        """
        Cancel registered tasks, wait for them, shutdown executors, run flushes.

        Args:
            timeout: Per-task cancellation wait timeout in seconds.
        """
        await self._cancel_tasks(timeout)
        self._shutdown_executors()
        await self._run_flushes()

    async def _cancel_tasks(self, timeout: float) -> None:
        for task, name in reversed(self._tasks):
            if task.done():
                continue
            logger.info("Cancelling background task: %s", name)
            task.cancel()
            done, _ = await asyncio.wait([task], timeout=timeout)
            if task in done:
                exc = task.exception() if not task.cancelled() else None
                if exc:
                    logger.warning("Task raised on cancellation (%s): %s", name, exc)
                else:
                    logger.debug("Task cancelled cleanly: %s", name)
            else:
                logger.warning("Task did not stop within %.1fs: %s", timeout, name)

    def _shutdown_executors(self) -> None:
        for executor in self._executors:
            try:
                executor.shutdown(wait=True)
                logger.debug("Executor shut down: %s", repr(executor))
            except Exception as exc:  # noqa: BLE001
                logger.warning("Executor shutdown raised: %s", exc)

    async def _run_flushes(self) -> None:
        for fn, name in self._flushes:
            logger.debug("Running flush: %s", name)
            try:
                result = fn()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as exc:  # noqa: BLE001
                logger.warning("Flush callable raised (%s): %s", name, exc)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def pending_task_count(self) -> int:
        return sum(1 for t, _ in self._tasks if not t.done())

    @property
    def registered_flush_count(self) -> int:
        return len(self._flushes)

    @property
    def registered_executor_count(self) -> int:
        return len(self._executors)
