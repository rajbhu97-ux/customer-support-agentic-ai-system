"""
Generates synthetic payment records linked to orders.

One order → one payment (1:1 relationship).
Payment status is set from order context but can be overridden
by the failure scenario generator to create broken states like:
  - payment SUCCESS but order FAILED  (ghost payment)
  - payment CHARGEBACK after DELIVERED (fraud scenario)
"""

import random

from mock_data_generator.utils.faker_helpers import (
    payment_id,
    datetime_after,
    iso,
    weighted_choice,
)
from mock_data_generator.utils.state_machine import OrderStatus, PaymentStatus


PAYMENT_METHODS = ["CREDIT_CARD", "DEBIT_CARD", "PAYPAL", "APPLE_PAY", "GOOGLE_PAY", "BANK_TRANSFER"]

# Map order status → likely payment status (normal path)
ORDER_TO_PAYMENT: dict[str, str] = {
    OrderStatus.PENDING.value:    PaymentStatus.PENDING.value,
    OrderStatus.CONFIRMED.value:  PaymentStatus.SUCCESS.value,
    OrderStatus.PROCESSING.value: PaymentStatus.SUCCESS.value,
    OrderStatus.SHIPPED.value:    PaymentStatus.SUCCESS.value,
    OrderStatus.DELIVERED.value:  PaymentStatus.SUCCESS.value,
    OrderStatus.CANCELLED.value:  PaymentStatus.REFUNDED.value,
    OrderStatus.FAILED.value:     PaymentStatus.FAILED.value,
    OrderStatus.RETURNED.value:   PaymentStatus.REFUNDED.value,
}

CARD_NETWORKS = ["VISA", "MASTERCARD", "AMEX", "DISCOVER"]


def generate_payment(order: dict) -> dict:
    order_created = order["created_at"]
    # Payment is usually processed minutes after order creation
    from datetime import datetime
    order_dt = datetime.strptime(order_created, "%Y-%m-%dT%H:%M:%SZ")
    paid_at = datetime_after(order_dt, min_hours=0, max_hours=1)

    payment_status = ORDER_TO_PAYMENT.get(order["status"], PaymentStatus.PENDING.value)
    method = random.choice(PAYMENT_METHODS)

    card_last4 = None
    card_network = None
    if method in ("CREDIT_CARD", "DEBIT_CARD"):
        card_last4 = str(random.randint(1000, 9999))
        card_network = random.choice(CARD_NETWORKS)

    # Occasionally simulate a gateway retry (realistic)
    retry_count = random.choices([0, 1, 2], weights=[85, 12, 3])[0]

    return {
        "payment_id": payment_id(),
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "status": payment_status,
        "method": method,
        "amount_usd": order["total_usd"],
        "currency": "USD",
        "card_last4": card_last4,
        "card_network": card_network,
        "gateway": random.choice(["STRIPE", "PAYPAL", "BRAINTREE", "ADYEN"]),
        "gateway_transaction_id": f"TXN-{weighted_choice({'A': 50, 'B': 50})}{random.randint(100000, 999999)}",
        "retry_count": retry_count,
        "paid_at": iso(paid_at),
        "created_at": iso(paid_at),
        "updated_at": iso(paid_at),
    }


def generate_payments(orders: list[dict]) -> list[dict]:
    """One payment per order."""
    return [generate_payment(order) for order in orders]
