from backend.models.enums import CircuitState
import time

class CircuitBreaker:

    def __init__(self, failure_threshold = 5):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = 15
        self._failure_count = 0
        self._state = CircuitState.CLOSED
        self._last_failure_time = None

    def can_execute(self) -> bool:
        if self._last_failure_time > self.recovery_timeout:
            self._state = CircuitState.HALF_OPEN
        return self._state == CircuitState.CLOSED

    def record_success(self) -> None:
        self._failure_count = 0
        self._state = CircuitState.CLOSED

    def record_failure(self) -> None:
        self._failure_count += 1
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            self._last_failure_time = time.monotonic()

    @property
    def state(self) -> CircuitState:
        return self._state

