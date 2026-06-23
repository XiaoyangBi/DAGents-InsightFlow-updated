import asyncio
import logging
from collections.abc import Coroutine
from typing import Any


logger = logging.getLogger(__name__)
_DETACHED_TASKS: set[asyncio.Task[Any]] = set()


def launch_detached_task(coro: Coroutine[Any, Any, Any], *, label: str) -> asyncio.Task[Any]:
    """Launch a long-running task outside FastAPI BackgroundTasks.

    Starlette BackgroundTasks are tied to the response lifecycle and will block
    dev-server reload shutdown while long workflows are still running. Detached
    asyncio tasks avoid that coupling.
    """

    task = asyncio.create_task(coro, name=label)
    _DETACHED_TASKS.add(task)

    def _finalize(done: asyncio.Task[Any]) -> None:
        _DETACHED_TASKS.discard(done)
        try:
            done.result()
        except asyncio.CancelledError:
            logger.info("Detached task cancelled: %s", done.get_name())
        except Exception:
            logger.exception("Detached task failed: %s", done.get_name())

    task.add_done_callback(_finalize)
    return task
