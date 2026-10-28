import re

SUPPORTED_INTENT = [
    "ORDER_STATUS",
    "ORDER_CANCEL",
    "ORDER_MODIFY",
    "RETURN_REQUEST",
    "REFUND_REQUEST",
    "PAYMENT_ISSUE",
    "PRODUCT_INQUIRY",
    "SHIPPING_ISSUE",
    "ACCOUNT_ISSUE",
    "COMPLAINT",
    "ESCALATION_REQUEST",
    "OTHER"
]

SUPPORTED_URGENCY = [
    "HIGH",
    "MEDIUM",
    "LOW"
]

SUPPORTED_SENTIMENT = [
    "POSITIVE",
    "NEUTRAL",
    "NEGATIVE"
]

SUPPORTED_STATUS = [
    "resolved",
    "escalated",
    "needs_clarification"
]

REQUIRED_FIELD_BY_INTENT = {  
    "ORDER_STATUS": ["order_id"],
    "ORDER_CANCEL": ["order_id"],
    "ORDER_MODIFY": ["order_id"],
    "RETURN_REQUEST": ["order_id", "product_name"],
    "REFUND_REQUEST": ["order_id", "amount"],
    "PAYMENT_ISSUE": ["order_id", "amount"],
    "PRODUCT_INQUIRY": ["product_name"],
    "SHIPPING_ISSUE": ["order_id"],
    "ACCOUNT_ISSUE": [],
    "COMPLAINT": [],
    "ESCALATION_REQUEST": [],
    "OTHER": []
}

SENSITIVE_PATTERNS = {
    "API_KEY": re.compile(r"(?i)\bapi[_-]?key\s*[:=]\s*\S+"),
    "ACCESS_TOKEN": re.compile(r"(?i)\baccess[_-]?token\s*[:=]\s*\S+"),
    "PASSWORD": re.compile(r"(?i)\bpassword\s*[:=]\s*\S+")
}