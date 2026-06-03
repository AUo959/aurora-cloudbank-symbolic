"""Async task safety utilities for Aurora CloudBank Symbolic.

Provides fire_and_forget() — a wrapper around asyncio.create_task() that
prevents silent GC cancellation and ensures exceptions are logged rather
than swallowed.

Background: asyncio.create_task() returns a Task that must be kept alive by
a strong reference. Without one, CPython may GC the task before it completes
— a silent, non-deterministic failure. Additionally, exceptions inside a
fire-and-forget task only surface as "Task exception was never retrieved"
warnings unless a done-callback is attached.
"""

import asyncio
import logging
from typing import Coroutine, Optional, Set

_logger = logging.getLogger(__name__)


def fire_and_forget(
    coro: Coroutine,
    *,
    name: str = "fire-and-forget",
    pending_tasks: Optional[Set[asyncio.Task]] = None,
    logger: Optional[logging.Logger] = None,
) -> asyncio.Task:
    """Schedule *coro* as a background Task safely.

    Differences from a bare asyncio.create_task():
    - Stores the Task in *pending_tasks* (if provided) to prevent GC.
    - Removes itself from *pending_tasks* when done (via done-callback).
    - Logs any unhandled exception at ERROR level instead of silently losing it.

    Args:
        coro: Coroutine to schedule.
        name: Human-readable task name (visible in debug traces).
        pending_tasks: Caller-owned set used to hold a strong reference. Pass
            ``self._pending_tasks`` from the owning class. If ``None``, a
            module-level fallback set is used — still safe, but the caller
            cannot inspect or cancel the task.
        logger: Logger to use for exception reporting. Defaults to this
            module's logger.

    Returns:
        The created asyncio.Task.
    """
    _log = logger or _logger
    task = asyncio.create_task(coro, name=name)

    _tasks = pending_tasks if pending_tasks is not None else _fallback_tasks

    _tasks.add(task)

    def _done(t: asyncio.Task) -> None:
        _tasks.discard(t)
        if not t.cancelled() and t.exception() is not None:
            _log.error(
                "Unhandled exception in background task %r: %s",
                t.get_name(),
                t.exception(),
                exc_info=t.exception(),
            )

    task.add_done_callback(_done)
    return task


# Module-level fallback set for callers that do not supply their own.
# Prevents GC even when the caller ignores the returned Task.
_fallback_tasks: Set[asyncio.Task] = set()
