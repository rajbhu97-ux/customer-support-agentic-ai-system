
import asyncio
from dataclasses import dataclass
from typing import Callable, Awaitable, TypeVar
import random

from backend.resilience.exception_classifier import ExceptionClassifier

T = TypeVar("T")

@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 10.0
    exponential_base: float = 2.0
    jitter: bool = True
    overall_timeout: float = 30.0


class RetryExecutor:

    def __init__(self, config: RetryConfig, classifier: ExceptionClassifier):
        self.config = config
        self.classifier = classifier

    
    def _calculate_delay(self, attempt: int) -> float:
        base_delay = self.config.base_delay * (self.config.exponential_base ** 2)
        delay = min(base_delay, self.config.max_delay)
        if self.config.jitter:
            delay = random.uniform(0, delay)
        return delay


    async def execute(
        self,
        operation: Callable[[], Awaitable[T]],
        *,
        breaker= None
    ) -> T:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + self.config.overall_timeout

        for attempt in range(1, self.config.max_attempts + 1):
            remaining = deadline - loop.time()
            if remaining < 0:
                raise RetryDeadlineExceed("Overall retry deadline exceed")
            try:
                async def operation_with_timeout():
                    return await asyncio.wait_for(
                        operation(),
                        timeout=remaining
                    )
                if breaker is not None:
                    return await breaker.call(operation_with_timeout)
                return await operation_with_timeout()
            except asyncio.CancelledError:
                raise
            except Exception as exe:
                decision = self.classifier.classify(exe)
                if not decision.retryable:
                    raise
                if attempt >= self.config.max_attempts:
                    raise
                delay = self._calculate_delay(attempt)
                if decision.retry_after is not None:
                    delay = max(delay, decision.retry_after)
                    
                remaining = deadline - loop.time()

                if delay >= remaining:
                    raise RetryDeadlineExceed(
                        "Insufficient time remaining for retry"
                    )
                await asyncio.sleep(delay)
        raise RuntimeError("Unexpected retry execution state")
