import uuid
from langchain_core.tools import tool

from backend.infrastructure.dynamodb import DynamoDBRepository


@tool
def create_ticket(
    customer_id: str,
    order_id: str,
    category: str,
    subject: str,
    description: str,
    priority: str = "MEDIUM",
) -> dict:
    """Create a support ticket."""
    try:
        table = DynamoDBRepository()
        ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
        ticket = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "order_id": order_id,
            "category": category,
            "subject": subject,
            "priority": priority,
            "status": "OPEN",
        }
        return table.create_ticket(ticket=ticket)
    except Exception as e:
        return {"error": f"Failed to create ticket", "success": False}

@tool
def escalate_ticket():
    pass



