
from backend.models.agent_state import State
from backend.guardrails.output_validator import validate_classification, validate_required_fields, validate_action_consistency, validate_state_consistancy, validate_sensitive_output, validate_final_response
from backend.guardrails.report.validation_report import ValidationReport

def get_agent_state():
    return State(
        user_message = "Where is my order?",
        raw_user_message = "test",
        intent = "ORDER_STATUS",
        confidence = 1.0,
        urgency = "MEDIUM",
        sentiment = "POSITIVE",
        status = "needs_clarification"
    )


def test_validate_classification_valid_input():
    report = ValidationReport()
    state = get_agent_state()
    result = validate_classification(state, report)
    assert result == None
    assert report.issues == []


def test_validate_classification_with_unknown_intent():
    report = ValidationReport()
    expected_output = [{'code': 'INVALID_INTENT', 'message': "Intent UNKNOWN is not supported. Must be one of ['ORDER_STATUS', 'ORDER_CANCEL', 'ORDER_MODIFY', 'RETURN_REQUEST', 'REFUND_REQUEST', 'PAYMENT_ISSUE', 'PRODUCT_INQUIRY', 'SHIPPING_ISSUE', 'ACCOUNT_ISSUE', 'COMPLAINT', 'ESCALATION_REQUEST', 'OTHER']", 'stage': 'classification', 'severity': 'critical'}]
    state = get_agent_state()
    state["intent"] = "UNKNOWN"
    result = validate_classification(state, report)
    assert result == None
    assert report.issues == expected_output

def test_validate_classification_with_unsupported_urgency():
    report = ValidationReport()
    state = get_agent_state()
    expected_output = [{'code': 'INVALID_URGENCY', 'message': "Urgency UNKNOWN is not supported. Must be one of ['HIGH', 'MEDIUM', 'LOW']", 'stage': 'classification', 'severity': 'recoverable'}]
    state["urgency"] = "UNKNOWN"
    result = validate_classification(state, report)
    assert result == None
    assert report.issues == expected_output


def test_validate_classification_with_unsupported_sentement():
    report = ValidationReport()
    state = get_agent_state()
    expected_output = [{'code': 'INVALID_SENTIMENT', 'message': "Sentiment UNKNOWN is not supported. Must be one of ['POSITIVE', 'NEUTRAL', 'NEGATIVE']", 'stage': 'classification', 'severity': 'recoverable'}]
    state["sentiment"] = "UNKNOWN"
    result = validate_classification(state, report)
    assert result == None
    assert report.issues == expected_output


def test_validate_classification_with_unsupported_confidence():
    report = ValidationReport()
    state = get_agent_state()
    expected_output = [{'code': 'INVALID_CONFIDENCE', 'message': 'Confidence 1.0 is not a number between 0 to 1', 'stage': 'classification', 'severity': 'critical'}]
    state["confidence"] = "1.0"
    result = validate_classification(state, report)
    assert result == None
    assert report.issues == expected_output


def test_validate_classification_with_unsupported_status():
    report = ValidationReport()
    state = get_agent_state()
    expected_output = [{'code': 'INVALID_STATUS', 'message': "Status unknown is not supported. Must be one of ['resolved', 'escalated', 'needs_clarification']", 'stage': 'classification', 'severity': 'critical'}]
    state["status"] = "unknown"
    result = validate_classification(state, report)
    assert result == None
    assert report.issues == expected_output