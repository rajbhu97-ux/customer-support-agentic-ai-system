import math
import re

from backend.models.agent_state import State
from backend.guardrails.report.validation_report import ValidationReport
from backend.guardrails.runtime_validator import ActionTakenModel
from backend.guardrails.utils.utils import SUPPORTED_INTENT, SUPPORTED_URGENCY, SUPPORTED_SENTIMENT, SUPPORTED_STATUS, REQUIRED_FIELD_BY_INTENT, SENSITIVE_PATTERNS


def validate_classification(state: State, report: ValidationReport) -> None:

    intent = state.get("intent")
    confidence = state.get("confidence")
    urgency = state.get("urgency")
    sentiment = state.get("sentiment")
    status = state.get("status")

    if intent not in SUPPORTED_INTENT:
        report.add(
            "INVALID_INTENT",
            f"Intent {intent} is not supported. Must be one of {SUPPORTED_INTENT}",
            "classification"
        )
        return 
    if urgency not in SUPPORTED_URGENCY:
        report.add(
            "INVALID_URGENCY",
            f"Urgency {urgency} is not supported. Must be one of {SUPPORTED_URGENCY}",
            "classification",
            severity="recoverable"
        )
    if sentiment not in SUPPORTED_SENTIMENT:
        report.add(
            "INVALID_SENTIMENT",
            f"Sentiment {sentiment} is not supported. Must be one of {SUPPORTED_SENTIMENT}",
            "classification",
            severity="recoverable"
        )

    if (
        not isinstance(confidence, (int, float))
        or isinstance(confidence, bool)
        or not math.isfinite(confidence)
        or not 0 <= confidence <= 1
    ):
        report.add(
            "INVALID_CONFIDENCE",
            f"Confidence {confidence} is not a number between 0 to 1",
            "classification"
        )
        return 
    
    if status not in SUPPORTED_STATUS:
        report.add(
            "INVALID_STATUS",
            f"Status {status} is not supported. Must be one of {SUPPORTED_STATUS}",
            "classification"
        )
        return 
    

def validate_required_fields(state: State, report: ValidationReport) -> None:
    intent = state.intent
    entities = state.entities

    required_fields = REQUIRED_FIELD_BY_INTENT.get(intent, [])

    for field in required_fields:
        value = entities.get(field, None)
        if value is None:
            report.add(
                "MISSING_REQUIRED_FIELD",
                f"Required field {field} is unavailable",
                "required_fields",
                severity="recoverable"
            )
        if isinstance(value, str) and not value.strip():
            report.add(
                "EMPTY_REQUIRED_FIELD",
                f"Required field {field} is empty",
                "required_fields",
                severity="recoverable"
            )


def validate_action_consistency(state: State, report: ValidationReport) -> None:
    actions = state.actions_taken
    data = state.data_for_response

    if actions:
        if not isinstance(actions, list):
            report.add(
                "INVALID_ACTION_FORMAT",
                "Actions taken must be a list",
                "tool_consistency"
            )
        for action in actions:
            try:
                validated_action = ActionTakenModel.model_validate(action)
            except Exception:
                report.add(
                    "INVALID_ACTION_TAKEN",
                    f"Action {action} is not valid",
                    "tool_consistency"
                )
                continue
            if validated_action.tool == "initiated_refund" and data.refund_status == "completed":
                 report.add(
                    "INCONSISTENT_ACTION_AND_DATA",
                    "Refund is already completed but action initiated_refund is present",
                    "tool_consistency"
                 )


def validate_sensitive_output(message: str, report: ValidationReport) -> None:

    for key, pattern in SENSITIVE_PATTERNS.items():
        if pattern.search(message):
            report.add(
                "SENSITIVE_INFORMATION_LEAK",
                f"Potential sensitive information found: {key}",
                "output_validation"
            )
            

def validate_final_response(message: str, report: ValidationReport) -> None:
    if not isinstance(message, str) or not message.strip():
        report.add(
            "INVALID_FINAL_RESPONSE",
            "Final response must be a non-empty string",
            "final_response"
        )
        return
    if len(message) > 5000:
        report.add(
            "FINAL_RESPONSE_TOO_LONG",
            "Final response must be less than 5000 characters",
            "final_response"
        )
    forbidden_markers = ["traceback (most recent call last)", "aws_secret_access_key", "internal system prompt"]

    for marker in forbidden_markers:
        if marker in message.lower():
            report.add(
                "FORBIDDEN_CONTENT_IN_RESPONSE",
                f"Response contains forbidden content: {marker}",
                "final_response"
            )
            break
    validate_sensitive_output(message, report)


def validate_state_consistancy(state: State, report: ValidationReport) -> None:
    status = state.status
    escalation_reason = state.escalation_reason
    hitl_decision = state.hitl_decision
    
    if status == "escalated" and not escalation_reason:
        report.add(
            "MISSING_ESCALATION_REASON",
            "Escalation reason is required when status is escalated",
            "state_consistency"
        )

    allowed_hitl_decisions = ["approved", "rejected", "pending"]
    if (hitl_decision is not None and hitl_decision not in allowed_hitl_decisions):
        report.add(
            "INVALID_HITL_DECISION",
            f"HITL decision {hitl_decision} is not supported. Must be one of {allowed_hitl_decisions}",
            "state_consistency"
         )
    if hitl_decision == "pending" and status == "completed":
        report.add(
            "INCONSISTENT_HITL_DECISION_AND_STATUS",
            "HITL decision cannot be pending when status is completed",
            "state_consistency"
        )
    
