from langchain_core.tools import tool
from backend.infrastructure.dynamodb import DynamoDBRepository


@tool
def lookup_customer(customer_id: str) -> dict:
    """Look up a customer by ID. Returns customer profile."""
    try:
        table = DynamoDBRepository()
        customer = table.get_customer(customer_id=customer_id)
        if not customer:
            return {"error": "Customer not found"}
        return customer
    except Exception as e:
        return {"error": f"Unable to fetch customer error: {str(e)}"}


@tool
def get_customer_tier(customer_id: str) -> dict:
    """Get the membership tier for a customer."""
    try:
        table = DynamoDBRepository()
        customer = table.get_customer(customer_id=customer_id)
        if not customer:
            return {"error": "Customer not found"}
        return {"customer_id": customer_id, "tier": customer["tier"]}
    except Exception as e:
        return {"error": f"Unable to fetch customer error: {str(e)}"}
