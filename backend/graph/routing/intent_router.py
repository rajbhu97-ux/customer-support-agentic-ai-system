from backend.graph.routing.error_router import route_after_node
from backend.models.agent_state import State

INTENT_TO_AGENT = {
    "ORDER_STATUS": "order_agent",
    "ORDER_CANCEL": "order_agent",
    "ORDER_MODIFY": "order_agent",
    "RETURN_REQUEST": "refund_agent",
    "REFUND_REQUEST": "refund_agent",
    "PAYMENT_ISSUE": "refund_agent",
    "PRODUCT_INQUIRY": "order_agent",
    "SHIPPING_ISSUE": "shipping_agent",
    "ACCOUNT_ISSUE": "order_agent",
    "COMPLAINT": "order_agent",
    "ESCALATION_REQUEST": "order_agent",
    "OTHER": "order_agent",
}


def route_by_intent(state):
    intent = state.get("intent", "OTHER")
    return INTENT_TO_AGENT.get(intent, "order_agent")


def route_after_intent_agent(state):
    post_node = route_after_node(state)
    if post_node != "continue":
        return post_node
    return route_by_intent(state)
