

class CircuitBreakerOpenError(Exception):

    def __init__(self, name, retry_after):
        self.name = name
        self.retry_after = retry_after

        super().__init__(
            f"{name} Circuit is OPEN. Please retry after {retry_after} time"
        )

    