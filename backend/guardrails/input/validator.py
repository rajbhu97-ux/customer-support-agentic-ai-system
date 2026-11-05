
from backend.guardrails.report import ValidationReport
from backend.guardrails.input.sanitizer import normalize_input, mask_sensitive_input
from backend.guardrails.input.patterns import COMPILED_INJECTION_PATTERNS
from backend.models.agent_state import State


def validate_input(state: State, report: ValidationReport) -> None:

    message = state.get("raw_user_message")

    if not isinstance(message, str):
        report.add(
            "INVALID_INPUT_FORMAT",
            "Input should be string",
            "invalid_input",
            severity="recoverable"
        )
        return None
        
    if not message.strip():
        report.add(
            "EMPTY_INPUT",
            "Input should not be empty",
            "invalid_input",
            severity="recoverable"
        )
        return None

    if len(message) > 1000:
        report.add(
            "TOO_LONG_INPUT",
            "Input message is too long",
            "invalid_input",
            severity="recoverable"
        )
        return None
    
    if len(message.encode("utf-8")) > 4000:
        report.add(
            "TOO_LONG_INPUT_BYTES",
            "Input message is too long in bytes",
            "invalid_input",
            severity="recoverable"
        )
        return None

    for pattern in COMPILED_INJECTION_PATTERNS:
        if pattern.search(message):
            report.add(
                "POTENTIAL_INJECTION_ATTACK",
                "Potential injection attack detected",
                "security_alert",
                severity="critical"
            )
            return None
    
    _, detected_pii = mask_sensitive_input(normalized_message)

    if detected_pii:
        report.add(
            "SENSITIVE_DATA_DETECTED",
            f"Sensitive data detected: {', '.join(detected_pii)}",
            "data_masking",
            severity="warning"
        )
        return None
