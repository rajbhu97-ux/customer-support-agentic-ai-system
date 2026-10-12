"""
State machine for valid and intentionally invalid state transitions.

This is the core of the failure scenario system.
Each entity (order, payment, shipment, refund) has a set of valid states
and rules about which combinations are realistic vs broken.

The agent will later need to reason about these broken states.
"""

from enum import Enum
from typing import NamedTuple


# ── Status Enums ──────────────────────────────────────────────────────────────

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    RETURNED = "RETURNED"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"
    DISPUTED = "DISPUTED"
    CHARGEBACK = "CHARGEBACK"


class ShipmentStatus(str, Enum):
    NOT_CREATED = "NOT_CREATED"
    LABEL_CREATED = "LABEL_CREATED"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    FAILED_DELIVERY = "FAILED_DELIVERY"
    RETURNED_TO_SENDER = "RETURNED_TO_SENDER"
    LOST = "LOST"
    UNKNOWN = "UNKNOWN"


class RefundStatus(str, Enum):
    NONE = "NONE"
    REQUESTED = "REQUESTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_CUSTOMER = "PENDING_CUSTOMER"
    PENDING_INTERNAL = "PENDING_INTERNAL"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"


class CustomerTier(str, Enum):
    STANDARD = "STANDARD"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


class TicketPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TicketCategory(str, Enum):
    ORDER_ISSUE = "ORDER_ISSUE"
    PAYMENT_ISSUE = "PAYMENT_ISSUE"
    SHIPMENT_ISSUE = "SHIPMENT_ISSUE"
    REFUND_REQUEST = "REFUND_REQUEST"
    PRODUCT_ISSUE = "PRODUCT_ISSUE"
    ACCOUNT_ISSUE = "ACCOUNT_ISSUE"
    GENERAL_INQUIRY = "GENERAL_INQUIRY"
    COMPLAINT = "COMPLAINT"


# ── Normal state combinations (happy path) ────────────────────────────────────

class SystemState(NamedTuple):
    """Snapshot of the state of one order and all related entities."""
    order_status: OrderStatus
    payment_status: PaymentStatus
    shipment_status: ShipmentStatus
    refund_status: RefundStatus


# Valid happy-path progressions
NORMAL_STATES: list[SystemState] = [
    SystemState(OrderStatus.PENDING,    PaymentStatus.PENDING,   ShipmentStatus.NOT_CREATED,    RefundStatus.NONE),
    SystemState(OrderStatus.CONFIRMED,  PaymentStatus.SUCCESS,   ShipmentStatus.NOT_CREATED,    RefundStatus.NONE),
    SystemState(OrderStatus.PROCESSING, PaymentStatus.SUCCESS,   ShipmentStatus.LABEL_CREATED,  RefundStatus.NONE),
    SystemState(OrderStatus.SHIPPED,    PaymentStatus.SUCCESS,   ShipmentStatus.IN_TRANSIT,     RefundStatus.NONE),
    SystemState(OrderStatus.DELIVERED,  PaymentStatus.SUCCESS,   ShipmentStatus.DELIVERED,      RefundStatus.NONE),
    SystemState(OrderStatus.CANCELLED,  PaymentStatus.REFUNDED,  ShipmentStatus.NOT_CREATED,    RefundStatus.COMPLETED),
    SystemState(OrderStatus.RETURNED,   PaymentStatus.REFUNDED,  ShipmentStatus.RETURNED_TO_SENDER, RefundStatus.COMPLETED),
]


# ── Failure state combinations (what the agent must reason about) ─────────────

class FailureScenario(NamedTuple):
    name: str
    description: str
    state: SystemState
    expected_agent_action: str   # what a correct agent should decide


FAILURE_SCENARIOS: list[FailureScenario] = [
    FailureScenario(
        name="ghost_payment",
        description="Payment succeeded but order creation failed. Customer was charged but has no order.",
        state=SystemState(
            OrderStatus.FAILED,
            PaymentStatus.SUCCESS,
            ShipmentStatus.NOT_CREATED,
            RefundStatus.NONE,
        ),
        expected_agent_action="Initiate full refund immediately. Do not ask customer to re-order.",
    ),
    FailureScenario(
        name="lost_in_transit",
        description="Order shipped, shipment status unknown or lost. Customer claims non-delivery.",
        state=SystemState(
            OrderStatus.SHIPPED,
            PaymentStatus.SUCCESS,
            ShipmentStatus.LOST,
            RefundStatus.NONE,
        ),
        expected_agent_action="File carrier claim and offer reship or refund within SLA window.",
    ),
    FailureScenario(
        name="delivered_but_disputed",
        description="Carrier says delivered, customer says not received.",
        state=SystemState(
            OrderStatus.DELIVERED,
            PaymentStatus.SUCCESS,
            ShipmentStatus.DELIVERED,
            RefundStatus.REQUESTED,
        ),
        expected_agent_action="Escalate to human review with photo proof request. Do not auto-refund.",
    ),
    FailureScenario(
        name="duplicate_refund_risk",
        description="Two refund requests exist for same order. Risk of double refund.",
        state=SystemState(
            OrderStatus.RETURNED,
            PaymentStatus.PARTIALLY_REFUNDED,
            ShipmentStatus.RETURNED_TO_SENDER,
            RefundStatus.UNDER_REVIEW,
        ),
        expected_agent_action="Flag duplicate refund risk. Put second request on hold pending review.",
    ),
    FailureScenario(
        name="payment_disputed_after_delivery",
        description="Order delivered. Customer filed chargeback with bank after receiving item.",
        state=SystemState(
            OrderStatus.DELIVERED,
            PaymentStatus.CHARGEBACK,
            ShipmentStatus.DELIVERED,
            RefundStatus.NONE,
        ),
        expected_agent_action="Escalate to fraud review team. Do not issue refund while chargeback is open.",
    ),
    FailureScenario(
        name="shipment_unknown_payment_success",
        description="Payment succeeded, order confirmed, but shipment tracking shows unknown state.",
        state=SystemState(
            OrderStatus.SHIPPED,
            PaymentStatus.SUCCESS,
            ShipmentStatus.UNKNOWN,
            RefundStatus.NONE,
        ),
        expected_agent_action="Contact carrier API. If no update in 48h, initiate reship or refund.",
    ),
    FailureScenario(
        name="refund_failed_after_approval",
        description="Refund was approved but payment gateway failed to process it.",
        state=SystemState(
            OrderStatus.CANCELLED,
            PaymentStatus.SUCCESS,
            ShipmentStatus.NOT_CREATED,
            RefundStatus.FAILED,
        ),
        expected_agent_action="Retry refund via alternate gateway. Notify customer of delay. Do not close ticket.",
    ),
    FailureScenario(
        name="order_cancelled_but_shipped",
        description="Customer cancelled order but warehouse already shipped it.",
        state=SystemState(
            OrderStatus.CANCELLED,
            PaymentStatus.SUCCESS,
            ShipmentStatus.IN_TRANSIT,
            RefundStatus.REQUESTED,
        ),
        expected_agent_action="Intercept with carrier if possible. If not, initiate return label and refund on receipt.",
    ),
    FailureScenario(
        name="partial_delivery",
        description="Multi-item order: some items delivered, some missing.",
        state=SystemState(
            OrderStatus.SHIPPED,
            PaymentStatus.SUCCESS,
            ShipmentStatus.DELIVERED,
            RefundStatus.NONE,
        ),
        expected_agent_action="Calculate partial refund for missing items. Reship or refund missing items only.",
    ),
    FailureScenario(
        name="refund_completed_payment_not_updated",
        description="Refund shows COMPLETED but payment record still shows SUCCESS. System inconsistency.",
        state=SystemState(
            OrderStatus.RETURNED,
            PaymentStatus.SUCCESS,
            ShipmentStatus.RETURNED_TO_SENDER,
            RefundStatus.COMPLETED,
        ),
        expected_agent_action="Flag as data inconsistency. Verify with payment gateway. Do not refund again.",
    ),
]


# ── Helper functions ──────────────────────────────────────────────────────────

def is_consistent_state(state: SystemState) -> bool:
    """
    Returns True if the state combination is a normal/expected progression.
    Returns False if it is a failure/inconsistent state.
    """
    return state in NORMAL_STATES


def get_failure_scenario_by_name(name: str) -> FailureScenario | None:
    for scenario in FAILURE_SCENARIOS:
        if scenario.name == name:
            return scenario
    return None


def all_failure_scenario_names() -> list[str]:
    return [s.name for s in FAILURE_SCENARIOS]
