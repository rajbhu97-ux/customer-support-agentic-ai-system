from backend.models.agent_state import State


def rejection_node(state: State):
    error = state.get("error_info", {})
    issues = state.get("validation_result", {}).get("issues", [])
    reason = error.get("message") or (issues[0]["message"] if issues else "")
    return {
        "final_response": f"I'm sorry, I can't process that request. {reason}".strip(),
        "status": "rejected",
        "node_status": "success",
    }


def human_review_node(state: State):
    error = state.get("error_info", {})
    return {
        "final_response": "Your message has been flagged for review by our team. We'll get back to you shortly.",
        "status": "escalated",
        "escalation_reason": error.get("message", "Flagged for human review"),
        "node_status": "success",
    }
