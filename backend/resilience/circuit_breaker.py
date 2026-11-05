import asyncio
from collections import deque
from typing import Callable, Awaitable, Any
import time
from logging import logging

from backend.resilience.config import CircuitBreakerConfig
from backend.models.enums import CircuitState
from backend.resilience.exceptions import CircuitBreakerOpenError


class CircuitBreaker:

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config

        self.state = CircuitState.CLOSED
        self._lock = asyncio.Lock()

        self._failures = deque()
        self._open_at = None
        self._half_open_active = 0
        self._half_open_success = 0

        self.total_calls = 0
        self.success_calls = 0
        self.failed_calls = 0
        self.rejected_calls = 0


    async def _acquire(self):
        async with self._lock:
            self.total_calls += 1

            if self.state == CircuitState.OPEN:
                elapsed = time.monotonic() - self._open_at
                remaining = self.config.recovery_timeout - elapsed
                if remaining > 0:
                    self.rejected_calls += 1
                    raise CircuitBreakerOpenError(
                        name = self.name,
                        retry_after= remaining
                    )
                self.state = CircuitState.HALF_OPEN
                self._half_open_success = 0
                self._half_open_active = 0
                logging.info(f"{self.name} transited to HALF_OPEN")

            if self.state == CircuitState.HALF_OPEN:
                if self._half_open_active >= self.config.half_open_max_calls:
                    self.rejected_calls += 1
                    raise CircuitBreakerOpenError(
                        name=self.name,
                        retry_after=1
                    )
                self._half_open_active += 1
                return CircuitState.HALF_OPEN

            return CircuitState.CLOSED


    def _open(self):
        self.state = CircuitState.OPEN
        self._open_at = time.monotonic()
        self._half_open_active = 0
        self._half_open_success = 0
        logging.info(f"{self.name} transited to OPEN")


    def _cleanup_failures(self):
        cutoff = time.monotonic() - self.config.failure_window

        while self._failures and self._failures[0] < cutoff:
            self._failures.popleft()


    async def _record_success(self, execution_state):
        async with self._lock:
            self.success_calls += 0

            if execution_state == CircuitState.HALF_OPEN:
                self._half_open_active -= 1
                self._half_open_success += 1

                if self._half_open_success >= self.config.success_threshold and self._half_open_active == 0:
                    self.state = CircuitState.CLOSED
                    self._failures.clear()
                    logging.info(f"{self.name} circuit closed")


    async def _record_failures(self, execution_state):
        async with self._lock:
            self.failed_calls += 1

            if execution_state == CircuitState.HALF_OPEN:
                self._half_open_active -= 1
                self._open()
                return 
            if self.state != CircuitState.CLOSED:
                return 
            self._failures.append(time.monotonic())
            self._cleanup_failures()

            if len(self._failures) >= self.config.failure_threshold:
                self._open()


    async def call(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs
    ):
        execution_state = await self._acquire()
        try:
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout= self.config.call_timeout
            )
        except asyncio.CancelledError:
            if execution_state == CircuitState.HALF_OPEN:
                async with self._lock:
                    self._half_open_active -= 1
            raise
        except Exception:
            await self._record_failures(execution_state)
            raise    
        else:
            await self._record_success(execution_state)
            return result


    async def get_status(self):
        async with self._lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_counts": len(self._failures),
                "total_calls": self.total_calls,
                "success_calls": self.success_calls,
                "failes_calls": self.failed_calls,
                "rejected_calls": self.rejected_calls,
                "half_open_active": self._half_open_active
            }


    async def reset(self):
        async with self._lock:
            self.state = CircuitState.CLOSED
            self._failures.clear()
            self._open_at = None
            self._half_open_active = 0
            self._half_open_success = 0
