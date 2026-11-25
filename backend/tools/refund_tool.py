import uuid

from langchain_core.tools import tool
from backend.infrastructure.dynamodb import DynamoDBRepository


@tool
def initiate_refund(order_id: str, amount: float, reason: str) -> dict:
    """Initiate a refund for an order."""
    try:
        table = DynamoDBRepository()
        refund = table.get_refund(order_id=order_id)
        existing = (
            refund
            if refund.get("status") in ("PROCESSING", "COMPLETED", "APPROVED")
            else None
        )
        if existing:
            return {
                "error": f"Refund already exists: {existing['refund_id']} ({existing['status']})",
                "success": False,
            }
        refund_id = f"REF-{uuid.uuid4().hex[:6].upper()}"
        data = {
            "refund_id": refund_id,
            "order_id": order_id,
            "amount_usd": amount,
            "status": "PROCESSING",
            "reason": reason,
        }
        try:
            return table.create_refund(data)
        except Exception as e:
            return {
                "error": f"Failed to create the refund for order: {order_id} error: {str(e)}",
                "success": False,
            }
    except Exception as e:
        return {
            "error": f"Failed to get the refund for order: {order_id} error: {str(e)}"
        }


@tool
def check_refund_status(order_id: str) -> dict:
    """Check payment and refund status for an order."""
    try:
        table = DynamoDBRepository()
        payment = table.get_payment(order_id=order_id)
        refund = table.get_refund(order_id=order_id)
        return {
            "order_id": order_id,
            "payment": (
                {"status": payment["status"], "amount": payment["amount_usd"]}
                if payment
                else None
            ),
            "existing_refund": (
                {"refund_id": refund["refund_id"], "status": refund["status"]}
                if refund
                else None
            ),
        }
    except Exception as e:
        return {
            "error": f"Failed to get the refund or payment for order: {order_id} error: {str(e)}"
        }
