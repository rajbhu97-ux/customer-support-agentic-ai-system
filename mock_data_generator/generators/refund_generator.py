"""
Generates synthetic refund records.

Only a subset of orders have refunds (cancelled, returned, or disputed).
Refund records are the most complex because they involve 3 systems:
  - order system (what was ordered)
  - payment system (how much was paid)
  - refund system (how much was returned)

Inconsistencies between these three are major failure scenarios.
"""

import random
from datetime import datetime

from mock_data_generator.utils.faker_helpers import (
    refund_id,
    datetime_after,
    iso,
    weighted_choice,
)
from mock_data_generator.utils.state_machine import OrderStatus, RefundStatus


# Orders with these statuses are candidates for refunds
REFUNDABLE_STATUSES = {
    OrderStatus.CANCELLED.value,
    OrderStatus.RETURNED.value,
    OrderStatus.FAILED.value,
}

REFUND_REASONS = [
    "Item not received",
    "Item damaged on arrival",
    "Wrong item delivered",
    "Item not as described",
    "Changed mind",
    "Duplicate order",
    "Defective product",
    "Order cancelled by customer",
    "Order cancelled by system",
    "Payment failure — customer charged",
]

# Normal refund status distribution
REFUND_STATUS_WEIGHTS = {
    RefundStatus.COMPLETED.value:     60,
    RefundStatus.UNDER_REVIEW.value:  15,
    RefundStatus.APPROVED.value:      10,
    RefundStatus.REJECTED.value:       8,
    RefundStatus.PROCESSING.value:     5,
    RefundStatus.FAILED.value:         2,
}


def generate_refund(order: dict, payment_amount: float) -> dict | None:
    """Returns None if this order doesn't qualify for a refund."""
    if order["status"] not in REFUNDABLE_STATUSES:
        return None

    order_dt = datetime.strptime(order["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    requested_at = datetime_after(order_dt, min_hours=1, max_hours=72)

    refund_status = weighted_choice(REFUND_STATUS_WEIGHTS)

    # Partial refunds happen sometimes (e.g. restocking fee deducted)
    is_partial = random.choices([True, False], weights=[20, 80])[0]
    if is_partial:
        refund_amount = round(payment_amount * random.uniform(0.5, 0.95), 2)
        deduction_reason = random.choice(["Restocking fee", "Return shipping deducted", "Partial use"])
    else:
        refund_amount = payment_amount
        deduction_reason = None

    completed_at = None
    if refund_status == RefundStatus.COMPLETED.value:
        completed_at = iso(datetime_after(requested_at, min_hours=24, max_hours=120))

    return {
        "refund_id": refund_id(),
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "status": refund_status,
        "reason": random.choice(REFUND_REASONS),
        "requested_amount_usd": payment_amount,
        "approved_amount_usd": refund_amount,
        "currency": "USD",
        "is_partial": is_partial,
        "deduction_reason": deduction_reason,
        "refund_method": random.choice(["ORIGINAL_PAYMENT_METHOD", "STORE_CREDIT", "BANK_TRANSFER"]),
        "gateway_refund_id": f"RFND-{random.randint(1000000, 9999999)}" if refund_status == RefundStatus.COMPLETED.value else None,
        "completed_at": completed_at,
        "requested_at": iso(requested_at),
        "created_at": iso(requested_at),
        "updated_at": iso(requested_at),
    }


def generate_refunds(orders: list[dict], payments: list[dict]) -> list[dict]:
    """Generate refunds for eligible orders using payment amount as the base."""
    # Build a lookup: order_id → payment amount
    payment_map = {p["order_id"]: p["amount_usd"] for p in payments}

    refunds = []
    for order in orders:
        amount = payment_map.get(order["order_id"], order["total_usd"])
        refund = generate_refund(order, amount)
        if refund:
            refunds.append(refund)

    return refunds
