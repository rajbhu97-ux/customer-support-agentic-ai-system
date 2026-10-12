"""
Generates synthetic product catalog.

Products have categories and price ranges that affect:
- refund eligibility (some categories are non-refundable)
- shipment method (heavy items → freight)
- support ticket category distribution
"""

import random

from mock_data_generator.utils.faker_helpers import (
    fake,
    product_id,
    price,
    weighted_choice,
)


CATEGORIES = {
    "ELECTRONICS":     {"min": 50,  "max": 1500, "refundable": True,  "weight": 20},
    "CLOTHING":        {"min": 15,  "max": 200,  "refundable": True,  "weight": 25},
    "BOOKS":           {"min": 5,   "max": 80,   "refundable": True,  "weight": 10},
    "HOME_APPLIANCES": {"min": 100, "max": 2000, "refundable": True,  "weight": 10},
    "SPORTS":          {"min": 20,  "max": 500,  "refundable": True,  "weight": 10},
    "BEAUTY":          {"min": 10,  "max": 150,  "refundable": False, "weight": 10},
    "FOOD":            {"min": 5,   "max": 100,  "refundable": False, "weight": 5},
    "TOYS":            {"min": 10,  "max": 200,  "refundable": True,  "weight": 5},
    "AUTOMOTIVE":      {"min": 20,  "max": 800,  "refundable": True,  "weight": 3},
    "SOFTWARE":        {"min": 10,  "max": 300,  "refundable": False, "weight": 2},
}

WEIGHT_MAP = {cat: v["weight"] for cat, v in CATEGORIES.items()}


def generate_product() -> dict:
    category = weighted_choice(WEIGHT_MAP)
    cfg = CATEGORIES[category]

    unit_price = price(cfg["min"], cfg["max"])
    stock = random.randint(0, 500)

    return {
        "product_id": product_id(),
        "name": fake.catch_phrase(),          # e.g. "Streamlined 4th generation firmware"
        "category": category,
        "unit_price_usd": unit_price,
        "currency": "USD",
        "sku": fake.bothify("SKU-????-####").upper(),
        "weight_kg": round(random.uniform(0.1, 20.0), 2),
        "is_refundable": cfg["refundable"],
        "stock_quantity": stock,
        "is_in_stock": stock > 0,
        "rating": round(random.uniform(2.5, 5.0), 1),
        "review_count": random.randint(0, 5000),
    }


def generate_products(n: int = 200) -> list[dict]:
    return [generate_product() for _ in range(n)]
