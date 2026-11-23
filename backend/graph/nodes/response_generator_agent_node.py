
from backend.models.agent_state import State
from backend.graph.nodes.safe_node import safe_node

@safe_node("response_generator", max_retries=1, fallback_response="Your request has been processed but I'm unable to generate a detailed response. Please contact support.")
def response_generator_agent_node(state: State):
    pass