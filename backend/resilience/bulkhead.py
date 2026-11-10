
import asyncio
from typing import Callable, Awaitable, TypeVar

from backend.resilience.config import BulkHeadConfig
from backend.resilience.exceptions import BulkHeadFullError, BulkHeadQueueTimeOutError

T = TypeVar("T")


class BulkHeadManager:

    def __init__(self, config: BulkHeadConfig):

        if config.max_concurrent < 1:
            raise ValueError("Minimum allowed call must be grater than zero")
        
        if config.max_wait < 0:
            raise ValueError("Maximum wait time cannot be negative")
        
        if config.queue_timeout < 0:
            raise ValueError("Concurrent timeout cannot be negative")

        self.config = config
        self._active = 0
        self._waiting = 0
        self._condition = asyncio.Condition()

    async def execute(
        self,
        operation: Callable[[], Awaitable[T]]
    ) -> T:
        async with self._condition:
            if self._active >= self.config.max_concurrent:
                if self._waiting >= self.config.max_wait:
                    raise BulkHeadFullError(
                        "Bulkhead capacity exhasted"
                    )
                self._waiting += 1
                try:
                    await asyncio.wait_for(
                        self._condition.wait_for(
                            lambda: self._active < self.config.max_concurrent 
                        ),
                        timeout=self.config.queue_timeout
                    )
                except TimeoutError as e:
                    raise BulkHeadQueueTimeOutError(
                        "BulkHead queue timeout exceeded"
                    ) from e
                finally:
                    self._waiting -= 1
            self._active += 1
            try:
                return await operation()
            finally:
                async with self._condition:
                    self._active -= 1
                    self._condition.notify(1)


    async def get_status(self) -> dict:
        async with self._condition:
            return {
                "max_concurrent": self.config.max_concurrent,
                "max_waiting": self.config.max_wait,
                "active": self._active,
                "waiting": self._waiting,
                "available": self.config.max_concurrent - self._active
            }
