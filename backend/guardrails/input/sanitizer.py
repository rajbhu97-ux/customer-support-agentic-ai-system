import unicodedata

from backend.guardrails.input.patterns import COMPILED_PII_PATTERNS


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

    for pattern, replacement in COMPILED_PII_PATTERNS:
        if pattern.search(message):
            detected_pii.append(replacement)
            message = pattern.sub(replacement, message)
    
    return message, detected_pii