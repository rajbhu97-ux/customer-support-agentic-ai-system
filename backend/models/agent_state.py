from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator
from typing import Optional


class EntitiesDict(TypedDict):
    order_id: Optional[str]
    product_name: Optional[str]
    amount: Optional[str]
    date: Optional[str]


class ActionTakenDict(TypedDict):
    tool: str
    result: str


class ValidationResult(TypedDict):
    is_valid: bool
    rejection_reason: Optional[str]
    sanitized_message: Optional[str]


class DataForResponse(TypedDict):
    order_id: Optional[str]
    order_status: Optional[str]
    action_taken: Optional[str]
    ticket_id: Optional[str]
    additional_info: Optional[str]
    refund_amount: Optional[str]
    refund_status: Optional[str]
    estimated_timeline: Optional[str]
    tracking_status: Optional[str]
    estimated_delivery: Optional[str]
    customer_tier: Optional[str]


class State(TypedDict):
    user_message: str
    raw_user_message: str
    conversation_history: Annotated[list[AnyMessage], operator.add]

    # Intent agent response
    intent: Optional[str]
    confidence: Optional[float]
    urgency: Optional[str]
    sentiment: Optional[str]
    entities: Optional[EntitiesDict]
    summary: Optional[str]

    # Domain agent
    status: Optional[str]
    actions_taken: Optional[list[ActionTakenDict]]
    resolution_summary: Optional[str]
    data_for_response: Optional[DataForResponse]
    escalation_reason: Optional[str]

    # Response generator agent
    final_response: Optional[str]

    step_count: Optional[int]
    validation_result: Optional[ValidationResult]
    hitl_decision: Optional[str]
    session_id: Optional[str]
