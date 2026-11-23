from backend.models.agent_state import State

CRITICAL_ERRORS = {
    "InjectionDetected",
    "RateLimitExceeded",
    "AuthenticationError",
    "ValidationError",
}


def route_after_node(state: State):
    status = state.get("node_status", "success")
    if status == "success":
        return "continue"
    elif status == "fallback":
        return "fallback"
    elif status == "retry":
        return "retry"
    elif status == "needs_review":
        return "human_review"
    return "reject"


def route_error_handler(state: State):
    error_info = state.get("error_info", {})
    error_type = error_info.get("error_type", "")

    if error_type in CRITICAL_ERRORS:
        return "reject"

    return "human_review"
