from backend.models.agent_state import State
from backend.graph.nodes.safe_node import safe_node


@safe_node(
    "intent_agent",
    max_retries=2,
    fallback_response="I'm having trouble understanding your request. Could you please rephrase?",
)
def intent_agent_node(state: State):
    pass
