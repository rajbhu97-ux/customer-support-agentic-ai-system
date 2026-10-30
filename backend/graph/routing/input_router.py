
from backend.models.agent_state import State
from backend.models.enums import InputDecision

def route_after_input_validation(state):

    decision = state.get("input_decision")

    if decision == InputDecision.CONTINUE.value:
        return "continue"
    
    if decision == InputDecision.REJECT.value:
        return "reject"

    if decision == InputDecision.HUMAN_REVIEW.value:
        return "human_review"