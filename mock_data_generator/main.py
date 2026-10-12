"""
Mock Data Generator — Main Runner

Run this once to generate all synthetic data for the project.

Usage:
    python -m mock_data_generator.main

Output:
    data/raw/customers.json        — 1,000 customers
    data/raw/products.json         — 200 products
    data/raw/orders.json           — 5,000 orders
    data/raw/payments.json         — 5,000 payments (1 per order)
    data/raw/shipments.json        — ~4,500 shipments (only shipped orders)
    data/raw/refunds.json          — ~1,200 refunds (eligible orders only)
    data/raw/tickets.json          — 2,000 support tickets
    data/raw/conversations.json    — 500 conversation histories
    data/raw/policies.json         — 8 policy documents
    data/raw/knowledge_base.json   — 13 KB articles
    data/scenarios/failure_scenarios.json — 200 failure scenario test cases
"""

import json
import time
from pathlib import Path

from mock_data_generator.generators.customer_generator import generate_customers
from mock_data_generator.generators.product_generator import generate_products
from mock_data_generator.generators.order_generator import generate_orders
from mock_data_generator.generators.payment_generator import generate_payments
from mock_data_generator.generators.shipment_generator import generate_shipments
from mock_data_generator.generators.refund_generator import generate_refunds
from mock_data_generator.generators.ticket_generator import generate_tickets
from mock_data_generator.generators.conversation_generator import generate_conversations
from mock_data_generator.generators.policy_generator import generate_policies
from mock_data_generator.generators.knowledge_base_generator import generate_knowledge_base
from mock_data_generator.scenarios.failure_scenario_generator import generate_failure_scenarios

RAW_DIR = Path("data/raw")
SCENARIOS_DIR = Path("data/scenarios")


def save(data: list[dict] | dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log(msg: str) -> None:
    print(f"  {msg}")


def main() -> None:
    print("\n=== Mock Data Generator ===\n")
    total_start = time.time()

    # ── Step 1: Customers ─────────────────────────────────────────────────────
    print("Generating customers...")
    start = time.time()
    customers = generate_customers(n=1000)
    save(customers, RAW_DIR / "customers.json")
    customer_ids = [c["customer_id"] for c in customers]
    log(f"{len(customers):,} customers  ({time.time() - start:.1f}s)")

    # ── Step 2: Products ──────────────────────────────────────────────────────
    print("Generating products...")
    start = time.time()
    products = generate_products(n=200)
    save(products, RAW_DIR / "products.json")
    product_ids = [p["product_id"] for p in products]
    log(f"{len(products):,} products  ({time.time() - start:.1f}s)")

    # ── Step 3: Orders ────────────────────────────────────────────────────────
    print("Generating orders...")
    start = time.time()
    orders = generate_orders(customer_ids=customer_ids, product_ids=product_ids, n=5000)
    save(orders, RAW_DIR / "orders.json")
    order_ids = [o["order_id"] for o in orders]
    log(f"{len(orders):,} orders  ({time.time() - start:.1f}s)")

    # ── Step 4: Payments ──────────────────────────────────────────────────────
    print("Generating payments...")
    start = time.time()
    payments = generate_payments(orders=orders)
    save(payments, RAW_DIR / "payments.json")
    log(f"{len(payments):,} payments  ({time.time() - start:.1f}s)")

    # ── Step 5: Shipments ─────────────────────────────────────────────────────
    print("Generating shipments...")
    start = time.time()
    shipments = generate_shipments(orders=orders)
    save(shipments, RAW_DIR / "shipments.json")
    log(f"{len(shipments):,} shipments  ({time.time() - start:.1f}s)")

    # ── Step 6: Refunds ───────────────────────────────────────────────────────
    print("Generating refunds...")
    start = time.time()
    refunds = generate_refunds(orders=orders, payments=payments)
    save(refunds, RAW_DIR / "refunds.json")
    log(f"{len(refunds):,} refunds  ({time.time() - start:.1f}s)")

    # ── Step 7: Support tickets ───────────────────────────────────────────────
    print("Generating support tickets...")
    start = time.time()
    tickets = generate_tickets(customers=customers, order_ids=order_ids, n=2000)
    save(tickets, RAW_DIR / "tickets.json")
    log(f"{len(tickets):,} tickets  ({time.time() - start:.1f}s)")

    # ── Step 8: Conversations ─────────────────────────────────────────────────
    print("Generating conversations...")
    start = time.time()
    conversations = generate_conversations(tickets=tickets, n=500)
    save(conversations, RAW_DIR / "conversations.json")
    log(f"{len(conversations):,} conversations  ({time.time() - start:.1f}s)")

    # ── Step 9: Policies ──────────────────────────────────────────────────────
    print("Generating policies...")
    start = time.time()
    policies = generate_policies()
    save(policies, RAW_DIR / "policies.json")
    log(f"{len(policies):,} policies  ({time.time() - start:.1f}s)")

    # ── Step 10: Knowledge base ───────────────────────────────────────────────
    print("Generating knowledge base...")
    start = time.time()
    kb = generate_knowledge_base()
    save(kb, RAW_DIR / "knowledge_base.json")
    log(f"{len(kb):,} KB articles  ({time.time() - start:.1f}s)")

    # ── Step 11: Failure scenarios ────────────────────────────────────────────
    print("Generating failure scenarios...")
    start = time.time()
    failure_scenarios = generate_failure_scenarios(
        orders=orders,
        customers=customers,
        payments=payments,
        shipments=shipments,
        refunds=refunds,
        n_per_scenario=20,
    )
    save(failure_scenarios, SCENARIOS_DIR / "failure_scenarios.json")
    log(f"{len(failure_scenarios):,} failure scenarios  ({time.time() - start:.1f}s)")

    # ── Summary ───────────────────────────────────────────────────────────────
    total = time.time() - total_start
    print(f"\n=== Done in {total:.1f}s ===\n")
    print("Output:")
    for path in sorted([*RAW_DIR.glob("*.json"), *SCENARIOS_DIR.glob("*.json")]):
        size_kb = path.stat().st_size / 1024
        print(f"  {path}  ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
