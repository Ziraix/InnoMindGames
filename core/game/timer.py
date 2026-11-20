import asyncio
from typing import Awaitable, Callable

_timers: dict[int, asyncio.Task] = {}


def register_timer(chat_id: int, task: asyncio.Task) -> None:
    old = _timers.pop(chat_id, None)
    if old is not None and not old.done() and old is not asyncio.current_task():
        old.cancel()
    _timers[chat_id] = task


def cancel_timer(chat_id: int) -> None:
    task = _timers.pop(chat_id, None)
    if task is not None and not task.done() and task is not asyncio.current_task():
        task.cancel()


async def delay(seconds: int, callback: Callable[[], Awaitable[None]]) -> None:
    await asyncio.sleep(seconds)
    await callback()