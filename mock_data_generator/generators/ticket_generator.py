"""
Generates synthetic customer support tickets.

Tickets are the primary entry point for the agent.
Each ticket has a category, priority, and status.
Some tickets reference orders/payments directly.
Ticket priority is influenced by customer tier.
"""

import random
from datetime import datetime

from mock_data_generator.utils.faker_helpers import (
    fake,
    ticket_id,
    past_datetime,
    datetime_after,
    iso,
    weighted_choice,
)
from mock_data_generator.utils.state_machine import (
    TicketStatus,
    TicketPriority,
    TicketCategory,
    CustomerTier,
)


# Ticket category distribution
CATEGORY_WEIGHTS = {
    TicketCategory.ORDER_ISSUE.value:      25,
    TicketCategory.SHIPMENT_ISSUE.value:   20,
    TicketCategory.REFUND_REQUEST.value:   20,
    TicketCategory.PAYMENT_ISSUE.value:    10,
    TicketCategory.PRODUCT_ISSUE.value:    10,
    TicketCategory.GENERAL_INQUIRY.value:   8,
    TicketCategory.ACCOUNT_ISSUE.value:     5,
    TicketCategory.COMPLAINT.value:         2,
}

# Ticket status distribution
STATUS_WEIGHTS = {
    TicketStatus.OPEN.value:             15,
    TicketStatus.IN_PROGRESS.value:      20,
    TicketStatus.PENDING_CUSTOMER.value: 10,
    TicketStatus.PENDING_INTERNAL.value:  5,
    TicketStatus.RESOLVED.value:         40,
    TicketStatus.CLOSED.value:            7,
    TicketStatus.ESCALATED.value:         3,
}

# Tier → priority boost (PLATINUM customers get URGENT more often)
TIER_PRIORITY_WEIGHTS: dict[str, dict[str, int]] = {
    CustomerTier.STANDARD.value: {
        TicketPriority.LOW.value: 30, TicketPriority.MEDIUM.value: 50,
        TicketPriority.HIGH.value: 15, TicketPriority.URGENT.value: 5,
    },
    CustomerTier.SILVER.value: {
        TicketPriority.LOW.value: 20, TicketPriority.MEDIUM.value: 50,
        TicketPriority.HIGH.value: 20, TicketPriority.URGENT.value: 10,
    },
    CustomerTier.GOLD.value: {
        TicketPriority.LOW.value: 10, TicketPriority.MEDIUM.value: 40,
        TicketPriority.HIGH.value: 30, TicketPriority.URGENT.value: 20,
    },
    CustomerTier.PLATINUM.value: {
        TicketPriority.LOW.value: 5, TicketPriority.MEDIUM.value: 25,
        TicketPriority.HIGH.value: 35, TicketPriority.URGENT.value: 35,
    },
}

# Sample ticket subjects by category
SUBJECTS: dict[str, list[str]] = {
    TicketCategory.ORDER_ISSUE.value: [
        "My order is missing items",
        "Order shows delivered but I never received it",
        "Wrong item was delivered",
        "Order is stuck in processing",
        "I want to cancel my order",
    ],
    TicketCategory.SHIPMENT_ISSUE.value: [
        "Tracking number not updating",
        "Package damaged on arrival",
        "Shipment delayed beyond estimated date",
        "Carrier says delivered but I see nothing",
        "My package was returned to sender",
    ],
    TicketCategory.REFUND_REQUEST.value: [
        "I need a refund for my order",
        "Refund not received after 10 days",
        "Partial refund amount is wrong",
        "I was charged twice, need refund",
        "Refund request was rejected unfairly",
    ],
    TicketCategory.PAYMENT_ISSUE.value: [
        "I was charged but my order failed",
        "Double charge on my card",
        "Payment declined but money was deducted",
        "I cannot update my payment method",
    ],
    TicketCategory.PRODUCT_ISSUE.value: [
        "Product stopped working after 2 days",
        "Product does not match description",
        "Missing parts in the box",
        "Product arrived broken",
    ],
    TicketCategory.GENERAL_INQUIRY.value: [
        "What is your return policy?",
        "How long does shipping take?",
        "Can I change my delivery address?",
        "Do you offer price matching?",
    ],
    TicketCategory.ACCOUNT_ISSUE.value: [
        "Cannot log in to my account",
        "My account was locked",
        "I want to delete my account",
    ],
    TicketCategory.COMPLAINT.value: [
        "Very poor customer service experience",
        "Agent was rude and unhelpful",
        "This is the third time I have this issue",
    ],
}


def generate_ticket(
    customer: dict,
    order_ids: list[str],
) -> dict:
    created_at = past_datetime(days_back=180)
    category = weighted_choice(CATEGORY_WEIGHTS)
    tier = customer.get("tier", CustomerTier.STANDARD.value)
    priority = weighted_choice(TIER_PRIORITY_WEIGHTS.get(tier, TIER_PRIORITY_WEIGHTS[CustomerTier.STANDARD.value]))
    status = weighted_choice(STATUS_WEIGHTS)

    subject = random.choice(SUBJECTS.get(category, ["General issue"]))

    resolved_at = None
    if status in (TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value):
        resolved_at = iso(datetime_after(created_at, min_hours=1, max_hours=72))

    return {
        "ticket_id": ticket_id(),
        "customer_id": customer["customer_id"],
        "order_id": random.choice(order_ids) if order_ids else None,
        "category": category,
        "priority": priority,
        "status": status,
        "subject": subject,
        "description": fake.paragraph(nb_sentences=3),
        "channel": random.choice(["CHAT", "EMAIL", "PHONE", "WEB_FORM"]),
        "assigned_agent": fake.name() if status != TicketStatus.OPEN.value else None,
        "escalated": status == TicketStatus.ESCALATED.value,
        "resolved_at": resolved_at,
        "created_at": iso(created_at),
        "updated_at": iso(datetime_after(created_at, min_hours=1, max_hours=48)),
    }


def generate_tickets(
    customers: list[dict],
    order_ids: list[str],
    n: int = 2000,
) -> list[dict]:
    return [
        generate_ticket(random.choice(customers), order_ids)
        for _ in range(n)
    ]
