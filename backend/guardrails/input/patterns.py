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