"""
Generates synthetic shipment records.

Only orders that reached SHIPPED or beyond get a shipment record.
Cancelled/failed orders have no shipment.

Shipment status can be broken by the failure scenario generator
to simulate lost packages, unknown tracking, failed delivery, etc.
"""

import random
from datetime import datetime

from mock_data_generator.utils.faker_helpers import (
    shipment_id,
    datetime_after,
    iso,
)
from mock_data_generator.utils.state_machine import OrderStatus, ShipmentStatus


CARRIERS = ["UPS", "FEDEX", "USPS", "DHL", "AMAZON_LOGISTICS"]

# Orders with these statuses get a shipment record
SHIPPED_STATUSES = {
    OrderStatus.SHIPPED.value,
    OrderStatus.DELIVERED.value,
    OrderStatus.RETURNED.value,
}

# Map order status → shipment status (normal path)
ORDER_TO_SHIPMENT: dict[str, str] = {
    OrderStatus.SHIPPED.value:   ShipmentStatus.IN_TRANSIT.value,
    OrderStatus.DELIVERED.value: ShipmentStatus.DELIVERED.value,
    OrderStatus.RETURNED.value:  ShipmentStatus.RETURNED_TO_SENDER.value,
}


def generate_shipment(order: dict) -> dict | None:
    """Returns None for orders that were never shipped."""
    if order["status"] not in SHIPPED_STATUSES:
        return None

    order_dt = datetime.strptime(order["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    shipped_at = datetime_after(order_dt, min_hours=24, max_hours=72)
    estimated_delivery = datetime_after(shipped_at, min_hours=48, max_hours=120)

    shipment_status = ORDER_TO_SHIPMENT.get(order["status"], ShipmentStatus.IN_TRANSIT.value)
    carrier = random.choice(CARRIERS)
    tracking_number = f"{carrier[:3].upper()}{random.randint(100000000, 999999999)}"

    actual_delivery = None
    if shipment_status == ShipmentStatus.DELIVERED.value:
        actual_delivery = iso(datetime_after(shipped_at, min_hours=48, max_hours=96))

    return {
        "shipment_id": shipment_id(),
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "status": shipment_status,
        "carrier": carrier,
        "tracking_number": tracking_number,
        "tracking_url": f"https://track.{carrier.lower()}.com/{tracking_number}",
        "origin": {
            "warehouse": f"WH-{random.choice(['EAST', 'WEST', 'CENTRAL'])}",
            "city": "Chicago",
            "state": "IL",
        },
        "destination": order["shipping_address"],
        "weight_kg": round(random.uniform(0.1, 15.0), 2),
        "shipping_method": random.choice(["STANDARD", "EXPRESS", "OVERNIGHT", "ECONOMY"]),
        "estimated_delivery": iso(estimated_delivery),
        "actual_delivery": actual_delivery,
        "shipped_at": iso(shipped_at),
        "created_at": iso(shipped_at),
        "updated_at": iso(shipped_at),
    }


def generate_shipments(orders: list[dict]) -> list[dict]:
    """Returns only shipments for orders that were actually shipped."""
    shipments = [generate_shipment(order) for order in orders]
    return [s for s in shipments if s is not None]
