
from backend.models.enums import InputDecision
from backend.guardrails.report import ValidationReport


def get_input_decision(report: ValidationReport) -> InputDecision:

    if report.has_critical_issue:
        return InputDecision.REJECT
    if report.has_recoverable_issue:
        return InputDecision.HUMAN_REVIEW

    return InputDecision.CONTINUE


