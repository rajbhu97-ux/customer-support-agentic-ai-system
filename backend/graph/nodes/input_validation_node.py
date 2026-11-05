
from backend.models.agent_state import State
from backend.guardrails.report.validation_report import ValidationReport
from backend.guardrails.input.input_decision import get_input_decision
from backend.models.enums import InputDecision
from backend.guardrails.input.sanitizer import normalize_input, mask_sensitive_input


def input_validation_node(state: State):

    report = ValidationReport()
    raw_message = state.get("raw_user_message")
    validate_input(state, report)

    decision = get_input_decision(report=report)

    if decision != InputDecision.CONTINUE:
        return {
            "input_decision": decision.value,
            "validation_result": report.to_dict()
        }
    normalized = normalize_input(raw_message)
    sanitized_message = mask_sensitive_input(normalized)
    return {
        "input_decision": decision.value,
        "input_message" : sanitized_message,
        "validation_result": report.to_dict()
    }