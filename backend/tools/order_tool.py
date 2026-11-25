from langchain_core.tools import tool
from backend.infrastructure.dynamodb import DynamoDBRepository


@tool
def get_order(order_id: str) -> dict:
    """Fetch order details by order ID."""
    try:
        table = DynamoDBRepository()
        order = table.get_order(order_id=order_id)
        if not order:
            return {"error": "Order not found", "success": False}
        return order
    except Exception as e:
        return {"error": f"Unable to fetch order error: {str(e)}", "success": False}


@tool
def get_orders_by_customer(customer_id: str) -> list[dict] | dict:
    """List all orders for a customer."""
    try:
        table = DynamoDBRepository()
        customer_order = table.get_customer_orders(customer_id=customer_id)
        if not customer_order:
            return {
                "error": f"Order not found for the given customer Id: {customer_id}",
                "success": False,
            }
        return customer_order
    except Exception as e:
        return {
            "error": f"Unable to fetch order for the given customer Id: {customer_id} error: {str(e)}",
            "success": False,
        }


@tool
def cancel_order(order_id: str) -> dict:
    """Cancel an order. Only works if status is PENDING or CONFIRMED."""
    try:
        table = DynamoDBRepository()
        order = table.get_order(order_id=order_id)
        if not order:
            return {"error": "Order not found", "success": False}
        if order["status"] in ("PENDING", "CONFIRMED"):
            try:
                table.update_order_status(order_id=order_id, new_status="CANCELLED")
                return {"order_id": order_id, "status": "CANCELLED", "success": True}
            except Exception as e:
                return {
                    "error": f"Unable to update order for the given order Id: {order_id} error: {str(e)}",
                    "success": False,
                }
        return {"error": f"Cannot cancel order in {order['status']} status", "success": False}
    except Exception as e:
        return {
            "error": f"Unable to fetch order for the given order Id: {order_id} error: {str(e)}",
            "success": False,
        }
        