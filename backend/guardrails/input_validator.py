
from models.agent_state import ValidationResult
import re

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
  

def _mask_pii(message: str):
    """Detect and replace PII patterns in the message with placeholder tokens.

    Iterates over predefined PII patterns (customer IDs, emails, phone numbers)
    and replaces any matches with corresponding placeholder tokens.

    Args:
        message (str): The input message to scan and mask.

    Returns:
        ValidationResult: A result containing:
            - is_valid (bool): Always True.
            - rejection_reason (None): Always None.
            - sanitized_message (str): The masked message if PII was found, else original message.
    """
    for pattern, replacement in COMPILED_PII_PATTERNS:
        message = pattern.sub(replacement, message)
    return ValidationResult(is_valid=True, rejection_reason=None, sanitized_message=message)


def validate_input(message: str) -> ValidationResult:
    """Validate and sanitize an incoming message by checking constraints and masking PII.

    Performs the following validations in order:
        1. Checks if the message is empty.
        2. Checks if the message is a string.
        3. Checks if the message exceeds 1000 characters.
    If all validations pass, delegates to mask_pii() to replace any detected PII.

    Args:
        message (str): The input message to validate and process.

    Returns:
        ValidationResult: A result containing:
            - is_valid (bool): True if all validations pass, False otherwise.
            - rejection_reason (str or None): Describes the validation failure if is_valid is False, else None.
            - sanitized_message (str): The PII-masked message if PII was found, else original message.

    Examples:
        >>> validate_input("Hi CUST-97376311, email: uowens@example.org")
        ValidationResult(is_valid=True, rejection_reason=None, sanitized_message='Hi [CUSTOMER_ID], email: [EMAIL]')

        >>> validate_input("")
        ValidationResult(is_valid=False, rejection_reason='Input should not be empty', sanitized_message=None)

        >>> validate_input("a" * 1001)
        ValidationResult(is_valid=False, rejection_reason='Input message is too long', sanitized_message=None)
    """
    if not isinstance(message, str):
        return ValidationResult(is_valid=False, rejection_reason="Input should be string", sanitized_message=None)
    if not message.strip():
        return ValidationResult(is_valid=False, rejection_reason="Input should not be empty", sanitized_message=None)
    if len(message) > 1000:
        return ValidationResult(is_valid=False, rejection_reason="Input message is too long", sanitized_message=None)
    for pattern in COMPILED_INJECTION_PATTERNS:
        if pattern.search(message):
            return ValidationResult(is_valid=False, rejection_reason="Potential injection attack detected", sanitized_message=None)
    return _mask_pii(message)
