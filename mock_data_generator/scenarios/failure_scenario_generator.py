"""
Failure Scenario Generator.

Takes existing orders, payments, shipments, and refunds and
intentionally corrupts a subset of them into known broken states.

This is the most important file for agent learning because:
  - Each scenario has a name and description
  - Each scenario has the broken system state
  - Each scenario has the CORRECT expected agent action
  - The agent must retrieve the right policy and produce the right action

How it works:
  1. Pick a random subset of orders
  2. For each order, pick a failure scenario from the state machine
  3. Override the order/payment/shipment/refund statuses to match the scenario
  4. Output a self-contained scenario document with all relevant context

The scenario documents go into data/scenarios/.
Later, the Streamlit scenario_tester.py page loads these and lets you
fire them at the agent and watch the reasoning.
"""

import random
import copy

from mock_data_generator.utils.state_machine import (
    FAILURE_SCENARIOS,
    FailureScenario,
)
from mock_data_generator.utils.faker_helpers import iso, past_datetime


def _find_payment(order_id: str, payments: list[dict]) -> dict | None:
    for p in payments:
        if p["order_id"] == order_id:
            return p
    return None


def _find_shipment(order_id: str, shipments: list[dict]) -> dict | None:
    for s in shipments:
        if s["order_id"] == order_id:
            return s
    return None


def _find_refund(order_id: str, refunds: list[dict]) -> dict | None:
    for r in refunds:
        if r["order_id"] == order_id:
            return r
    return None


def _find_customer(customer_id: str, customers: list[dict]) -> dict | None:
    for c in customers:
        if c["customer_id"] == customer_id:
            return c
    return None


def generate_failure_scenario(
    scenario_def: FailureScenario,
    order: dict,
    customers: list[dict],
    payments: list[dict],
    shipments: list[dict],
    refunds: list[dict],
) -> dict:
    """
    Build a self-contained failure scenario document.
    Overrides statuses to match the broken state defined in scenario_def.
    """
    # Deep-copy so we don't mutate the original data
    broken_order = copy.deepcopy(order)
    broken_order["status"] = scenario_def.state.order_status.value

    # Payment — find existing or create a stub
    existing_payment = _find_payment(order["order_id"], payments)
    broken_payment = copy.deepcopy(existing_payment) if existing_payment else {
        "payment_id": f"PAY-STUB-{order['order_id']}",
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "amount_usd": order["total_usd"],
        "currency": "USD",
        "method": "CREDIT_CARD",
        "gateway": "STRIPE",
        "gateway_transaction_id": "TXN-STUB",
        "created_at": order["created_at"],
        "updated_at": order["updated_at"],
    }
    broken_payment["status"] = scenario_def.state.payment_status.value

    # Shipment — find existing or create a stub
    existing_shipment = _find_shipment(order["order_id"], shipments)
    broken_shipment = copy.deepcopy(existing_shipment) if existing_shipment else {
        "shipment_id": f"SHIP-STUB-{order['order_id']}",
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "carrier": "UNKNOWN",
        "tracking_number": "N/A",
        "created_at": order["created_at"],
        "updated_at": order["updated_at"],
    }
    broken_shipment["status"] = scenario_def.state.shipment_status.value

    # Refund — find existing or create a stub
    existing_refund = _find_refund(order["order_id"], refunds)
    broken_refund = copy.deepcopy(existing_refund) if existing_refund else {
        "refund_id": f"REF-STUB-{order['order_id']}",
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "requested_amount_usd": order["total_usd"],
        "approved_amount_usd": None,
        "currency": "USD",
        "created_at": order["created_at"],
        "updated_at": order["updated_at"],
    }
    broken_refund["status"] = scenario_def.state.refund_status.value

    # Customer context
    customer = _find_customer(order["customer_id"], customers)

    return {
        "scenario_id": f"SCEN-{scenario_def.name.upper().replace('_', '-')}-{order['order_id']}",
        "scenario_name": scenario_def.name,
        "description": scenario_def.description,
        "expected_agent_action": scenario_def.expected_agent_action,
        "system_state": {
            "order_status": scenario_def.state.order_status.value,
            "payment_status": scenario_def.state.payment_status.value,
            "shipment_status": scenario_def.state.shipment_status.value,
            "refund_status": scenario_def.state.refund_status.value,
        },
        "is_consistent": False,  # All failure scenarios are inconsistent by definition
        "context": {
            "customer": customer,
            "order": broken_order,
            "payment": broken_payment,
            "shipment": broken_shipment,
            "refund": broken_refund,
        },
        "created_at": iso(past_datetime(days_back=30)),
    }


def generate_failure_scenarios(
    orders: list[dict],
    customers: list[dict],
    payments: list[dict],
    shipments: list[dict],
    refunds: list[dict],
    n_per_scenario: int = 20,
) -> list[dict]:
    """
    Generate n_per_scenario examples of each failure scenario.
    Total output = len(FAILURE_SCENARIOS) * n_per_scenario documents.
    With 10 scenarios and n=20, that's 200 failure scenario test cases.
    """
    scenarios = []
    order_pool = list(orders)  # copy so we can shuffle independently

    for scenario_def in FAILURE_SCENARIOS:
        # Pick a fresh random sample for each scenario type
        sample = random.sample(order_pool, min(n_per_scenario, len(order_pool)))
        for order in sample:
            doc = generate_failure_scenario(
                scenario_def=scenario_def,
                order=order,
                customers=customers,
                payments=payments,
                shipments=shipments,
                refunds=refunds,
            )
            scenarios.append(doc)

    return scenarios
