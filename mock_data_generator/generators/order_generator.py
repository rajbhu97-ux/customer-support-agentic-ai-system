"""
Generates synthetic orders linked to customers and products.

Most orders follow the happy path. A configurable fraction get
a failure state injected — these become test cases for the agent.

Key design decisions:
- Orders reference customer_ids and product_ids (foreign keys)
- order_status is set independently of payment/shipment here;
  the failure_scenario_generator will later create broken combinations
- created_at drives the timeline for all downstream events
"""

import random

from mock_data_generator.utils.faker_helpers import (
    fake,
    order_id,
    past_datetime,
    datetime_after,
    iso,
    weighted_choice,
)
from mock_data_generator.utils.state_machine import OrderStatus


# Normal order status distribution (happy path weights)
ORDER_STATUS_WEIGHTS = {
    OrderStatus.PENDING.value:    5,
    OrderStatus.CONFIRMED.value:  5,
    OrderStatus.PROCESSING.value: 5,
    OrderStatus.SHIPPED.value:    15,
    OrderStatus.DELIVERED.value:  60,
    OrderStatus.CANCELLED.value:  7,
    OrderStatus.RETURNED.value:   3,
}


def generate_order(customer_ids: list[str], product_ids: list[str]) -> dict:
    created_at = past_datetime(days_back=365)
    num_items = random.randint(1, 5)

    items = []
    subtotal = 0.0
    for _ in range(num_items):
        qty = random.randint(1, 3)
        unit_price = round(random.uniform(10.0, 300.0), 2)
        line_total = round(qty * unit_price, 2)
        subtotal += line_total
        items.append({
            "product_id": random.choice(product_ids),
            "quantity": qty,
            "unit_price_usd": unit_price,
            "line_total_usd": line_total,
        })

    subtotal = round(subtotal, 2)
    tax = round(subtotal * 0.08, 2)
    shipping_fee = round(random.choice([0.0, 4.99, 9.99, 14.99]), 2)
    total = round(subtotal + tax + shipping_fee, 2)

    status = weighted_choice(ORDER_STATUS_WEIGHTS)

    # Estimated delivery is 3–7 days after order creation
    estimated_delivery = datetime_after(created_at, min_hours=72, max_hours=168)

    return {
        "order_id": order_id(),
        "customer_id": random.choice(customer_ids),
        "status": status,
        "items": items,
        "item_count": num_items,
        "subtotal_usd": subtotal,
        "tax_usd": tax,
        "shipping_fee_usd": shipping_fee,
        "total_usd": total,
        "currency": "USD",
        "shipping_address": {
            "street": fake.street_address(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zip": fake.zipcode(),
            "country": "US",
        },
        "estimated_delivery": iso(estimated_delivery),
        "created_at": iso(created_at),
        "updated_at": iso(datetime_after(created_at, min_hours=1, max_hours=24)),
    }


def generate_orders(
    customer_ids: list[str],
    product_ids: list[str],
    n: int = 5000,
) -> list[dict]:
    return [generate_order(customer_ids, product_ids) for _ in range(n)]
