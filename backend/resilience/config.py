from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.resilience.retry import RetryExecutor
    from backend.resilience.bulkhead import BulkHeadExecutor
    from backend.resilience.circuit_breaker import CircuitBreaker
    from backend.resilience.timeout import TimeOutManager


@dataclass(frozen=True)
class CircuitBreakerConfig:

    failure_threshold: int = 5
    failure_window: float = 60

    success_threshold: int = 2
    recovery_timeout: float = 30
    half_open_max_calls: int = 1
    call_timeout: float = 15
    minimum_calls: int = 5
    

@dataclass(frozen=True)
class TimeOutConfig:

    timeout: float = 10.0


@dataclass(frozen=True)
class BulkHeadConfig:
    max_concurrent: int = 10
    max_wait: int = 20
    queue_timeout: float = 3.0


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 10.0
    exponential_base: float = 2.0
    jitter: bool = True
    overall_timeout: float = 30.0


@dataclass(frozen=True)
class DependencyResiliencePolicy:
    retry: RetryExecutor
    bulkhead: BulkHeadExecutor
    circuit_breaker: CircuitBreaker
    timeout: TimeOutManager

