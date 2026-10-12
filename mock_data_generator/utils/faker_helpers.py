"""
Shared Faker instance and common helpers used across all generators.
One Faker instance with a fixed seed so data is reproducible.
"""

import random
import uuid
from datetime import datetime, timedelta

from faker import Faker

# Fixed seed = reproducible data across runs
SEED = 42
fake = Faker("en_US")
Faker.seed(SEED)
random.seed(SEED)


# ── ID generators ─────────────────────────────────────────────────────────────

def customer_id() -> str:
    return f"CUST-{fake.bothify('########').upper()}"

def order_id() -> str:
    return f"ORD-{fake.bothify('#####').upper()}"

def payment_id() -> str:
    return f"PAY-{fake.bothify('#######').upper()}"

def shipment_id() -> str:
    return f"SHIP-{fake.bothify('######').upper()}"

def product_id() -> str:
    return f"PROD-{fake.bothify('####').upper()}"

def refund_id() -> str:
    return f"REF-{fake.bothify('######').upper()}"

def ticket_id() -> str:
    return f"TKT-{fake.bothify('######').upper()}"

def conversation_id() -> str:
    return f"CONV-{uuid.uuid4().hex[:8].upper()}"

def policy_id() -> str:
    return f"POL-{fake.bothify('###').upper()}"

def kb_article_id() -> str:
    return f"KB-{fake.bothify('####').upper()}"


# ── Date helpers ──────────────────────────────────────────────────────────────

def past_datetime(days_back: int = 365) -> datetime:
    """Return a random datetime within the last N days."""
    delta = random.randint(0, days_back * 24 * 60)  # minutes
    return datetime.utcnow() - timedelta(minutes=delta)

def future_datetime(days_ahead: int = 30) -> datetime:
    """Return a random datetime within the next N days."""
    delta = random.randint(0, days_ahead * 24 * 60)
    return datetime.utcnow() + timedelta(minutes=delta)

def datetime_after(base: datetime, min_hours: int = 1, max_hours: int = 48) -> datetime:
    """Return a datetime that is after `base` by a random number of hours."""
    delta = random.randint(min_hours * 60, max_hours * 60)
    return base + timedelta(minutes=delta)

def iso(dt: datetime) -> str:
    """Format datetime as ISO 8601 string."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Weighted random choice ────────────────────────────────────────────────────

def weighted_choice(choices: dict) -> str:
    """
    Choose a key from a dict where values are weights.
    Example: weighted_choice({"SUCCESS": 80, "FAILED": 20})
    """
    keys = list(choices.keys())
    weights = list(choices.values())
    return random.choices(keys, weights=weights, k=1)[0]


# ── Money helpers ─────────────────────────────────────────────────────────────

def price(min_val: float = 5.0, max_val: float = 500.0) -> float:
    """Return a realistic price rounded to 2 decimal places."""
    return round(random.uniform(min_val, max_val), 2)

def discount(original: float, pct: float) -> float:
    """Apply a percentage discount."""
    return round(original * (1 - pct / 100), 2)
