from backend.resilience.config import (
    DependencyResiliencePolicy,
    RetryConfig,
    BulkHeadConfig,
    CircuitBreakerConfig,
    TimeOutConfig,
)
from backend.resilience.retry import RetryExecutor
from backend.resilience.bulkhead import BulkHeadExecutor
from backend.resilience.circuit_breaker import CircuitBreaker
from backend.resilience.timeout import TimeOutManager
from backend.resilience.executor import ResilienceExecutor


order_policy = DependencyResiliencePolicy(
    retry=RetryExecutor(
        RetryConfig(max_attempts=3, base_delay=1.0, max_delay=5.0, overall_timeout=20.0)
    ),
    bulkhead=BulkHeadExecutor(
        BulkHeadConfig(max_concurrent=10, max_wait=20, queue_timeout=2.0)
    ),
    circuit_breaker=CircuitBreaker(
        CircuitBreakerConfig(failure_threshold=5, recovery_timeout=30)
    ),
    timeout=TimeOutManager(TimeOutConfig(timeout=5.0)),
)

refund_policy = DependencyResiliencePolicy(
    retry=RetryExecutor(RetryConfig()),
    bulkhead=BulkHeadExecutor(BulkHeadConfig(max_concurrent=5, max_wait=10)),
    circuit_breaker=CircuitBreaker(
        CircuitBreakerConfig(failure_threshold=5, recovery_timeout=30)
    ),
    timeout=TimeOutManager(TimeOutConfig(timeout=8.0)),
)

shipping_policy = DependencyResiliencePolicy(
    retry=RetryExecutor(RetryConfig()),
    bulkhead=BulkHeadExecutor(BulkHeadConfig(max_concurrent=5, max_wait=10)),
    circuit_breaker=CircuitBreaker(
        CircuitBreakerConfig(failure_threshold=5, recovery_timeout=30)
    ),
    timeout=TimeOutManager(TimeOutConfig(timeout=8.0)),
)

gemini_policy = DependencyResiliencePolicy(
    retry=RetryExecutor(RetryConfig()),
    bulkhead=BulkHeadExecutor(BulkHeadConfig(max_concurrent=5, max_wait=10)),
    circuit_breaker=CircuitBreaker(
        CircuitBreakerConfig(failure_threshold=10, recovery_timeout=15)
    ),
    timeout=TimeOutManager(TimeOutConfig(timeout=6.0)),
)


policies = {
    "order_api": order_policy,
    "refund_api": refund_policy,
    "shipping_api": shipping_policy,
    "gemini_ai": gemini_policy
}

resilience_executor = ResilienceExecutor(
    policies=policies
)