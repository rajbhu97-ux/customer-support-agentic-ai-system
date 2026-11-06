from dataclasses import dataclass

from backend.resilience.exceptions import DependencyTimeoutError, DependencyValidationError, DependencyUnavailableError, RateLimitError, AuthenticationError, RetryDeadlineExceed, CircuitBreakerOpenError

@dataclass(frozen=True)
class ExceptionDecision:
    retryable: bool
    count_as_dependency_failure: bool
    retry_after: float | None = None


class ExceptionClassifier:

    @staticmethod
    def classify(exception: Exception) -> ExceptionDecision:
        if isinstance(exception, CircuitBreakerOpenError):
            return ExceptionDecision(
                retryable=False,
                count_as_dependency_failure=False
            )
        if isinstance(exception, RateLimitError):
            return ExceptionDecision(
                retryable=True,
                count_as_dependency_failure=False,
                retry_after=exception.retry_after
            )
        if isinstance(exception, (DependencyTimeoutError, DependencyUnavailableError)):
            return ExceptionDecision(
                retryable=True,
                count_as_dependency_failure=True
            )
        if isinstance(exception, (AuthenticationError, DependencyValidationError)):
            return ExceptionDecision(
                retryable=False,
                count_as_dependency_failure=False
            )

        return ExceptionDecision(
            retryable=False,
            count_as_dependency_failure=False
        )
    
        
