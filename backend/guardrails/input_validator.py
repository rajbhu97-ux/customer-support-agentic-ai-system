
from backend.models.agent_state import ValidationResult
import re
from backend.guardrails.report.validation_report import ValidationReport

PATTERNS = {
    r'CUST-\d{8}': "[CUSTOMER_ID]",
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}': "[EMAIL]", 
    r'[\d]{3}[.-][\d]{3}[.-][\d]{4}(?:x\d+)?|[\d]{3}-[\d]{3}-[\d]{3}-[\d]{4}(?:x\d+)?': "[PHONE]"
    }

INJECTION_PATTERNS = [
      r"ignore\s+(previous|prior|above|all)\s+instructions",
      r"you\s+are\s+now",
      r"act\s+as\s+(a|an)",
      r"forget\s+(everything|all|your)",
      r"new\s+instructions?",
      r"system\s*:",
      r"<\s*system\s*>",
      r"jailbreak",
      r"do\s+anything\s+now",   # DAN prompt
  ]

COMPILED_INJECTION_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]
COMPILED_PII_PATTERNS = [(re.compile(pattern), r) for pattern, r in PATTERNS.items()]
  

def mask_sensitive_input(message: str):
    for pattern, replacement in COMPILED_PII_PATTERNS:
        message = pattern.sub(replacement, message)
    return message


def validate_input(message: str, report: ValidationReport) -> None:
    if not isinstance(message, str):
        return report.add(
            "INVALID_INPUT_FORMAT",
            "Input should be string",
            "invalid_input",
            severity="recoverable"
        )
    if not message.strip():
        return report.add(
            "EMPTY_INPUT",
            "Input should not be empty",
            "invalid_input",
            severity="recoverable"
        )
    if len(message) > 1000:
        return report.add(
            "TOO_LONG_INPUT",
            "Input message is too long",
            "invalid_input",
            severity="recoverable"
        )
    for pattern in COMPILED_INJECTION_PATTERNS:
        if pattern.search(message):
            return report.add(
                "POTENTIAL_INJECTION_ATTACK",
                "Potential injection attack detected",
                "security_alert",
                severity="critical"
            )
    return message
