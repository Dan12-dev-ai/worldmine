"""In-process event bus for service coordination and safe retries."""
import asyncio
import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], Any]]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._worker_started = False

    async def publish(self, topic: str, message: Dict[str, Any]) -> None:
        await self._queue.put((topic, message))
        if not self._worker_started:
            self._worker_started = True
            asyncio.create_task(self._dispatch_loop())

    async def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], Any]) -> None:
        self._subscribers.setdefault(topic, []).append(handler)

    async def _dispatch_loop(self) -> None:
        while True:
            topic, message = await self._queue.get()
            handlers = self._subscribers.get(topic, [])
            if not handlers:
                logger.debug("EventBus: no subscribers for topic %s", topic)
                continue
            for handler in handlers:
                try:
                    result = handler(message)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as exc:
                    logger.exception("EventBus handler failed for topic %s", topic)
            self._queue.task_done()

event_bus = EventBus()
