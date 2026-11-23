from backend.models.agent_state import State
from backend.guardrails.report import ValidationReport
from backend.guardrails.output.validator import (
    validate_classification,
    validate_required_fields,
    validate_action_consistency,
    validate_sensitive_output,
    validate_final_response,
    validate_state_consistancy,
)
import logging

logger = logging.getLogger(__name__)


def validate_intent_output(state: State) -> dict:
    report = ValidationReport()
    validate_classification(state, report)
    validate_required_fields(state, report)
    return _build_result(state, report, "intent_validation")


def validate_domain_output(state: State) -> dict:
    report = ValidationReport()
    validate_classification(state, report)
    validate_action_consistency(state, report)
    validate_state_consistancy(state, report)
    return _build_result(state, report, "domain_validation")


def validate_response_output(state: State) -> dict:
    report = ValidationReport()
    message = state.get("final_response", "")
    validate_final_response(message, report)
    validate_sensitive_output(state, report)
    return _build_result(state, report, "response_validation")


def _build_result(state: State, report: ValidationReport, stage: str) -> dict:
    if report.has_critical_issue:
        logger.error(f"[{stage}] critical issues: {report.to_dict()}")
        return {
            "node_status": "error",
            "current_node": stage,
            "error_info": {
                "node": stage,
                "error_type": "ValidationError",
                "message": report.issues[0].message,
            },
            "validation_result": report.to_dict(),
        }

    if report.has_recoverable_issue:
        logger.warning(f"[{stage}] recoverable issues: {report.to_dict()}")
        return {
            "node_status": "needs_review",
            "current_node": stage,
            "validation_result": report.to_dict(),
        }

    return {
        "node_status": "success",
        "current_node": stage,
        "validation_result": report.to_dict(),
    }
