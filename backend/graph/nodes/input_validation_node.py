
from backend.models.agent_state import State
from backend.guardrails.report.validation_report import ValidationReport
from backend.guardrails.input.input_decision import get_input_decision
from backend.models.enums import InputDecision

def input_validation_node(state: State):

    report = ValidationReport()
    raw_message = state.get("raw_user_message")
    sanitized_message = validate_input(raw_message, report)

    decision = get_input_decision(report=report)

    if decision != InputDecision.CONTINUE:
        return {
            "input_decision": decision.value,
            "validation_result": report.to_dict()
        }

    return {
        "input_decision": decision.value,
        "input_message" : sanitized_message,
        "validation_result": report.to_dict()
    }