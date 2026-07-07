"""Progress reporting during resume parsing."""

import asyncio
import contextlib
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any

ParseProgressCallback = Callable[[str, int, str], Awaitable[None]]


async def run_with_progress_heartbeat(
    operation: Coroutine[Any, Any, str],
    *,
    on_progress: ParseProgressCallback | None,
    stage: str,
    start_percent: int,
    end_percent: int,
    message: str,
    interval_seconds: float = 2.0,
) -> str:
    if on_progress is None:
        return await operation

    done = asyncio.Event()

    async def heartbeat() -> None:
        percent = start_percent
        while not done.is_set():
            await on_progress(stage, percent, message)
            percent = min(end_percent, percent + 3)
            try:
                await asyncio.wait_for(done.wait(), timeout=interval_seconds)
            except TimeoutError:
                continue

    task = asyncio.create_task(heartbeat())
    try:
        return await operation
    finally:
        done.set()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
