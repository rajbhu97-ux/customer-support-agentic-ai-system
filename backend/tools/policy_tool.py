from langchain_core.tools import tool


@tool
def check_policy(category: str, customer_tier: str = "STANDARD") -> dict:
    """Check applicable policies for a category and tier."""
    # matches = [p for p in get_policies() if p["category"] == category and customer_tier in p["applies_to_tiers"]]
    # if not matches:
    #     return {"error": f"No policy found for category={category}, tier={customer_tier}"}
    # return {"policies": matches}
    pass
