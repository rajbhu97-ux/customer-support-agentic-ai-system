
import re

SENSITIVE_PATTERNS = {
    "API_KEY": re.compile(r"(?i)\bapi[_-]?key\s*[:=]\s*\S+"),
    "ACCESS_TOKEN": re.compile(r"(?i)\baccess[_-]?token\s*[:=]\s*\S+"),
    "PASSWORD": re.compile(r"(?i)\bpassword\s*[:=]\s*\S+")
}