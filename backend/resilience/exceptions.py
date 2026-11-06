

class DependencyError(Exception):
    """Base exception for dependency failure"""


class DependencyTimeoutError(DependencyError):
    pass


class DependencyUnavailableError(DependencyError):
    pass


class RateLimitError(DependencyError):

    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after
        

class AuthenticationError(Exception):
    pass


class DependencyValidationError(Exception):
    pass


class RetryDeadlineExceed(Exception):
    pass


class CircuitBreakerOpenError(Exception):

    def __init__(self, name, retry_after):
        self.name = name
        self.retry_after = retry_after

        super().__init__(
            f"{name} Circuit is OPEN. Please retry after {retry_after} time"
        )

    