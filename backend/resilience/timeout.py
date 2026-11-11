import asyncio
from typing import Callable, TypeVar, Awaitable, ParamSpec

from backend.resilience.config import TimeOutConfig
from backend.resilience.exceptions import DependencyTimeoutError

T = TypeVar("T")
P = ParamSpec("P")


class TimeOutManager:

    def __init__(self, config: TimeOutConfig):
        if config.timeout <= 0:
            raise ValueError(f"Timeout must be greater than zero. currently {config.timeout}")

        self.config = config

    async def execute(
        self,
        operation: Callable[[], Awaitable[T]],
        timeout: float | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:

        actual_timeout = timeout if timeout is not None else self.config.timeout
        if actual_timeout <= 0:
            raise ValueError(f"Timeout should greater than 0. currently {actual_timeout}")
        try:
            result = await asyncio.wait_for(
                operation(*args, **kwargs), timeout=actual_timeout
            )
            return result
        except asyncio.CancelledError:
            raise
        except TimeoutError as e:
            raise DependencyTimeoutError(
                f"Dependency call exceeded {actual_timeout} sec"
            ) from e
