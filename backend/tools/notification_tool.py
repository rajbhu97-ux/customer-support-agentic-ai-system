from langchain_core.tools import tool


@tool
def send_notification(customer_id: str, message: str, channel: str = "EMAIL") -> dict:
    """Send a notification to the customer."""
    return {
        "customer_id": customer_id,
        "channel": channel,
        "sent": True,
        "message_preview": message[:100],
    }
