
from backend.models.agent_state import State
from backend.graph.nodes.safe_node import safe_node

@safe_node("order_agent", max_retries=2)
def order_agent_node(state: State):
    pass