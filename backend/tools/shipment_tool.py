from langchain_core.tools import tool
from backend.infrastructure.dynamodb import DynamoDBRepository


@tool
def lookup_shipment(order_id: str) -> dict:
    """Get shipment tracking info for an order."""
    try:
        table = DynamoDBRepository()
        shipment = table.get_shipment(order_id=order_id)
        if not shipment:
            return {
                "error": f"No shipment found for order {order_id}",
                "success": False,
            }
        return shipment
    except Exception as e:
        return {
            "error": f"Failed to find the shipment for order {order_id}",
            "success": False,
        }
