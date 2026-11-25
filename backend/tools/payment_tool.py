from langchain_core.tools import tool
from backend.infrastructure.dynamodb import DynamoDBRepository


@tool
def get_payment(order_id: str) -> dict:
    """Look up payment details for an order."""
    try:
        table = DynamoDBRepository()
        payment = table.get_payment(order_id=order_id)
        if not payment:
            return {"error": "Payment not found", "success": False}
        return payment
    except Exception as e:
        return {
            "error": f"Failed to get payment for order: {order_id} error: {str(e)}",
            "success": False,
        }
