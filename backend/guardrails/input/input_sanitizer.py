import unicodedata

from backend.guardrails.input.input_patterns import (
    COMPILED_INJECTION_PATTERNS,
    COMPILED_PII_PATTERNS,
)


def normalize_input(message: str) -> str:

    message = unicodedata.normalize("NFKC", message)

    message = "".join(
        char
        for char in message
        if char in "\n\t" or (char.isprintable() and unicodedata.category(char) != "Cf")
    )

    return " ".join(message.split())

def mask_sensitive_input(message: str):

    detected_pii = []

    for pii_type, (pattern, replacement) in COMPILED_PII_PATTERNS.items():
        if pattern.search(message):
            detected_pii.append(pii_type)
            message = pattern.sub(replacement, message)
    
    return message, detected_pii