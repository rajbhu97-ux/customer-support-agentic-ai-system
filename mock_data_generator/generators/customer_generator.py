"""
Generates synthetic customer records.

Each customer has a tier (STANDARD → PLATINUM) which affects:
- refund policy leniency
- auto-approval thresholds
- escalation priority

This matters for the agent: a PLATINUM customer gets faster resolution.
"""

import random
from datetime import datetime

from mock_data_generator.utils.faker_helpers import (
    fake,
    customer_id,
    past_datetime,
    iso,
    weighted_choice,
)
from mock_data_generator.utils.state_machine import CustomerTier


# Realistic tier distribution: most customers are STANDARD
TIER_WEIGHTS = {
    CustomerTier.STANDARD:  65,
    CustomerTier.SILVER:    20,
    CustomerTier.GOLD:      10,
    CustomerTier.PLATINUM:   5,
}

PREFERRED_CONTACT = ["EMAIL", "PHONE", "CHAT", "SMS"]


def generate_customer() -> dict:
    created_at = past_datetime(days_back=730)  # up to 2 years ago

    tier = weighted_choice({k.value: v for k, v in TIER_WEIGHTS.items()})

    # Platinum/Gold customers have longer history and higher lifetime value
    tier_multiplier = {
        CustomerTier.STANDARD.value: 1.0,
        CustomerTier.SILVER.value:   2.5,
        CustomerTier.GOLD.value:     6.0,
        CustomerTier.PLATINUM.value: 15.0,
    }[tier]

    lifetime_value = round(random.uniform(50, 500) * tier_multiplier, 2)
    total_orders = random.randint(1, int(10 * tier_multiplier))
    total_tickets = random.randint(0, max(1, total_orders // 3))

    return {
        "customer_id": customer_id(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "tier": tier,
        "address": {
            "street": fake.street_address(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zip": fake.zipcode(),
            "country": "US",
        },
        "preferred_contact": random.choice(PREFERRED_CONTACT),
        "lifetime_value_usd": lifetime_value,
        "total_orders": total_orders,
        "total_tickets": total_tickets,
        "is_active": random.choices([True, False], weights=[90, 10])[0],
        "created_at": iso(created_at),
        "updated_at": iso(past_datetime(days_back=30)),
    }


def generate_customers(n: int = 1000) -> list[dict]:
    return [generate_customer() for _ in range(n)]
