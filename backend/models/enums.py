from enum import Enum

class InputDecision(str, Enum):
    CONTINUE = "continue"
    REJECT = "reject"
    HUMAN_REVIEW = "human_review"


class ValidationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    RECOVERABLE = "recoverable"
    CRITICAL = "critical"

