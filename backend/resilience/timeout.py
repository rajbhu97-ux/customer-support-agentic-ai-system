
import asyncio
from typing import Callable, TypeVar, Awaitable

from backend.resilience.config import TimeOutConfig
from backend.resilience.exceptions import DependencyTimeoutError

T = TypeVar("T")

class TimeOutManager:

    def __init__(self, config: TimeOutConfig):
        if self.config.timeout <= 0:
            raise ValueError("Timeout must be greater than zero")

        self.config = config

    
    async def execute(
        self,
        operation: Callable[[], Awaitable[T]],
        *,
        timeout: float | None = None
    ) -> T:
        actual_timeout = timeout if timeout is not None else self.config.timeout
        if actual_timeout <= 0:
            raise ValueError("Timeout should greater than 0")
        try:
            result = await asyncio.wait_for(
                operation(),
                timeout= actual_timeout
            )
            return result
        except asyncio.CancelledError:
            raise
        except TimeoutError as e:
            raise DependencyTimeoutError(
                f"Dependency call exceeded {actual_timeout} sec"
            ) from e
