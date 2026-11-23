
from backend.models.agent_state import State
from backend.graph.nodes.safe_node import safe_node


@safe_node("refund_agent", max_retries=2)
def refund_agent_node(state: State):
    pass