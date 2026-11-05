
from typing import Protocol, Callable, Any


class CircuitBreakerProtocol(Protocol):

    async def call(
        self, 
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        ...
    
    async def get_status(self) -> dict:
        ...

    async def reset(self) -> None:
        ...