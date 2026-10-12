"""
Generates synthetic business policy documents.

Policies are the rules the agent must follow when making decisions.
They are stored as structured documents and will be loaded into the
RAG knowledge base in Phase 2.

Key policies the agent will reference:
- Refund window (30 days standard, 60 days GOLD/PLATINUM)
- Auto-approve thresholds (< $50 auto-approve for trusted customers)
- Escalation rules (URGENT + PLATINUM → human within 1 hour)
- Non-refundable categories (FOOD, BEAUTY, SOFTWARE)
"""

from mock_data_generator.utils.faker_helpers import policy_id


# Policies are static/structured — not randomly generated.
# We define them explicitly because they encode real business rules
# that the agent must retrieve and apply correctly.

POLICIES: list[dict] = [
    {
        "policy_id": policy_id(),
        "name": "Standard Return and Refund Policy",
        "category": "REFUND",
        "version": "2.1",
        "summary": "Customers may return eligible items within 30 days of delivery for a full refund.",
        "rules": [
            "Return window is 30 days from confirmed delivery date.",
            "Items must be in original condition and packaging.",
            "Non-refundable categories: FOOD, BEAUTY, SOFTWARE (digital), gift cards.",
            "Shipping cost is non-refundable unless the error was ours.",
            "Refunds are processed within 5–7 business days after item receipt.",
        ],
        "applies_to_tiers": ["STANDARD", "SILVER", "GOLD", "PLATINUM"],
        "auto_approve_below_usd": 50.0,
    },
    {
        "policy_id": policy_id(),
        "name": "Premium Member Extended Return Policy",
        "category": "REFUND",
        "version": "1.3",
        "summary": "GOLD and PLATINUM members enjoy an extended 60-day return window.",
        "rules": [
            "Return window is 60 days from confirmed delivery date for GOLD and PLATINUM tiers.",
            "Auto-approval limit is $200 for GOLD, $500 for PLATINUM.",
            "Free return shipping label is provided for PLATINUM members.",
            "Refunds are expedited within 2–3 business days.",
        ],
        "applies_to_tiers": ["GOLD", "PLATINUM"],
        "auto_approve_below_usd": 200.0,
    },
    {
        "policy_id": policy_id(),
        "name": "Ghost Payment Resolution Policy",
        "category": "PAYMENT",
        "version": "1.0",
        "summary": "If a payment succeeds but the order fails, a full refund must be issued within 24 hours.",
        "rules": [
            "If payment_status=SUCCESS and order_status=FAILED, initiate full refund immediately.",
            "Do not ask the customer to re-order. Apologize and refund.",
            "Refund must be processed within 24 hours of detection.",
            "Flag the incident for engineering review.",
            "Customer must receive an email notification with refund timeline.",
        ],
        "applies_to_tiers": ["STANDARD", "SILVER", "GOLD", "PLATINUM"],
        "auto_approve_below_usd": 9999.0,
    },
    {
        "policy_id": policy_id(),
        "name": "Lost or Missing Package Policy",
        "category": "SHIPMENT",
        "version": "1.2",
        "summary": "If a package is confirmed lost by the carrier, reship or refund within 5 business days.",
        "rules": [
            "Open a carrier claim if tracking shows LOST or no update for 7 days.",
            "Offer reship as first option. Offer refund if reship is not possible.",
            "Do not wait for carrier resolution before compensating the customer.",
            "PLATINUM customers get reship + refund if both requested.",
        ],
        "applies_to_tiers": ["STANDARD", "SILVER", "GOLD", "PLATINUM"],
        "auto_approve_below_usd": 150.0,
    },
    {
        "policy_id": policy_id(),
        "name": "Chargeback and Fraud Investigation Policy",
        "category": "FRAUD",
        "version": "1.1",
        "summary": "Do not issue refunds while a chargeback is open. Escalate to the fraud team.",
        "rules": [
            "If payment_status=CHARGEBACK, do not issue any refund.",
            "Escalate immediately to the fraud review team.",
            "Gather evidence: delivery confirmation, tracking, order history.",
            "Respond to bank dispute within 7 calendar days.",
            "Refund only after fraud team clears the case.",
        ],
        "applies_to_tiers": ["STANDARD", "SILVER", "GOLD", "PLATINUM"],
        "auto_approve_below_usd": 0.0,
    },
    {
        "policy_id": policy_id(),
        "name": "Escalation Policy",
        "category": "ESCALATION",
        "version": "2.0",
        "summary": "Defines when and how tickets must be escalated to a human agent.",
        "rules": [
            "URGENT priority tickets must be assigned to a human within 1 hour.",
            "PLATINUM customer tickets must receive a human response within 30 minutes.",
            "Any ticket open for more than 48 hours without resolution must be escalated.",
            "Agent confidence below 0.6 must trigger human review.",
            "Conflicting system states (e.g. two refund requests) must be escalated.",
        ],
        "applies_to_tiers": ["STANDARD", "SILVER", "GOLD", "PLATINUM"],
        "auto_approve_below_usd": 0.0,
    },
    {
        "policy_id": policy_id(),
        "name": "Duplicate Refund Prevention Policy",
        "category": "REFUND",
        "version": "1.0",
        "summary": "Detect and block duplicate refund requests before processing.",
        "rules": [
            "Before processing any refund, check for existing refund records on the same order.",
            "If a refund is already COMPLETED or PROCESSING, reject the new request.",
            "If a refund is PENDING or UNDER_REVIEW, put new request on hold.",
            "Alert the fraud team if the same customer submits 3+ refund requests in 30 days.",
        ],
        "applies_to_tiers": ["STANDARD", "SILVER", "GOLD", "PLATINUM"],
        "auto_approve_below_usd": 0.0,
    },
    {
        "policy_id": policy_id(),
        "name": "Partial Delivery Compensation Policy",
        "category": "SHIPMENT",
        "version": "1.0",
        "summary": "If only some items in a multi-item order are delivered, refund or reship the missing items.",
        "rules": [
            "Customer must provide a list of missing items.",
            "Calculate refund as the proportional value of missing items.",
            "Offer reship as an alternative to partial refund.",
            "If missing items total > $100, escalate for manual review.",
        ],
        "applies_to_tiers": ["STANDARD", "SILVER", "GOLD", "PLATINUM"],
        "auto_approve_below_usd": 100.0,
    },
]


def generate_policies() -> list[dict]:
    """Policies are static — return the pre-defined list."""
    return POLICIES
