
from dataclasses import dataclass

@dataclass(frozen=True)
class CircuitBreakerConfig:

    failure_threshold: int = 5
    failure_window: float = 60

    success_threshold: int = 2
    recovery_timeout: float = 30
    half_open_max_calls: int = 1
    call_timeout: float = 15
    minimum_calls: int = 5
    



