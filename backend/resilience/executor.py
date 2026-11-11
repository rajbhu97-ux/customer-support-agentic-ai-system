from typing import Callable, Awaitable, TypeVar, ParamSpec

T = TypeVar("T")
P = ParamSpec("P")


class ResilienceExecutor:

    def __init__(self, policies: dict[str, DependencyResiliencePolicy]):
        self.policies = policies

    async def execute(
        self,
        dependency: str,
        operation_name: str,
        operation: Callable[[], Awaitable[T]],
        *args: P.args,
        **kwargs: P.kwargs
    ) -> T:
        policy = self.policies.get(dependency)

        if policy is None:
            raise ValueError(f"No resilience policy found for dependency {dependency}")

        async def execute_attempt() -> T:
            async def execute_with_timeout() -> T:
                return await policy.timeout.execute(lambda: operation(*args, **kwargs))

            async def execute_with_circuit_breaker() -> T:
                return await policy.circuit_breaker.call(execute_with_timeout)

            return await policy.bulkhead.execute(execute_with_circuit_breaker)

        return await policy.retry.execute(execute_attempt)
