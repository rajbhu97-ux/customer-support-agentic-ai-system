"""
Generates synthetic conversation histories.

Conversations simulate real chat sessions between customers and support agents.
These serve two purposes:
  1. Training data for understanding what real conversations look like
  2. Context that the memory system will store and retrieve

Each conversation is linked to a ticket and contains a sequence of turns.
Some conversations are incomplete (customer dropped off) — another failure case.
"""

import random
from datetime import datetime

from mock_data_generator.utils.faker_helpers import (
    conversation_id,
    datetime_after,
    iso,
    weighted_choice,
)
from mock_data_generator.utils.state_machine import TicketCategory


# Conversation templates by category.
# Each template is a list of (role, message) tuples.
# role: "customer" or "agent"

CONVERSATION_TEMPLATES: dict[str, list[list[tuple[str, str]]]] = {
    TicketCategory.REFUND_REQUEST.value: [
        [
            ("customer", "Hi, I need a refund for my order."),
            ("agent", "Hi! I'd be happy to help. Could you please share your order ID?"),
            ("customer", "Sure, it's {order_id}."),
            ("agent", "Thank you. I can see your order was delivered on {date}. May I ask the reason for the refund?"),
            ("customer", "The item is defective. It stopped working after two days."),
            ("agent", "I'm sorry to hear that. I've initiated a full refund of ${amount}. You'll receive it in 5–7 business days. Is there anything else I can help you with?"),
            ("customer", "No, thank you."),
            ("agent", "Have a great day! Your ticket #{ticket_id} has been resolved."),
        ],
        [
            ("customer", "Where is my refund? I requested it 2 weeks ago."),
            ("agent", "I apologize for the delay. Let me look into this for you. What's your order ID?"),
            ("customer", "{order_id}"),
            ("agent", "I see a refund was approved on {date} but it appears the processing failed. I'm reinitiating it now. You'll receive it in 2–3 business days with my apologies."),
            ("customer", "This is the second time this has happened. Very frustrated."),
            ("agent", "I completely understand your frustration and I'm sorry. I've also added a $10 store credit to your account as an apology. Is there anything else?"),
            ("customer", "Ok fine. Thank you."),
        ],
    ],
    TicketCategory.SHIPMENT_ISSUE.value: [
        [
            ("customer", "My package says delivered but I never got it."),
            ("agent", "I'm sorry to hear that! Let me check the tracking for your order. What's your order ID?"),
            ("customer", "{order_id}"),
            ("agent", "I can see the carrier marked it as delivered at {date} at your front door. Can you check with neighbors or your building mailroom?"),
            ("customer", "Already checked. It's not there."),
            ("agent", "Understood. I've filed a missing package claim with the carrier. In the meantime, I'll arrange a reship. Expect it in 3–5 business days."),
            ("customer", "Thank you, I appreciate that."),
        ],
        [
            ("customer", "My tracking hasn't updated in 5 days. Is it lost?"),
            ("agent", "Let me check that for you. Order ID please?"),
            ("customer", "{order_id}"),
            ("agent", "I see the last scan was 5 days ago in Chicago. This sometimes happens but let me escalate to the carrier. I'll follow up with you within 24 hours."),
            ("customer", "Ok. What if it is lost?"),
            ("agent", "If we confirm it's lost, we'll reship or refund — whichever you prefer. You won't be left without a resolution."),
        ],
    ],
    TicketCategory.ORDER_ISSUE.value: [
        [
            ("customer", "I received the wrong item in my order."),
            ("agent", "I'm so sorry about that! Let me look up your order. What's the order ID?"),
            ("customer", "{order_id}"),
            ("agent", "I see you ordered {product}. What did you receive instead?"),
            ("customer", "Something completely different, not even the same category."),
            ("agent", "I sincerely apologize. I've arranged a replacement shipment and will email you a free return label for the incorrect item. No need to pay anything."),
            ("customer", "Great, thanks."),
        ],
    ],
    TicketCategory.PAYMENT_ISSUE.value: [
        [
            ("customer", "I was charged but my order failed. Where is my money?"),
            ("agent", "I'm very sorry about this. This should not happen. Let me investigate immediately. Order ID?"),
            ("customer", "{order_id}"),
            ("agent", "I can confirm: your payment of ${amount} was successful but the order failed on our end. I'm initiating a full refund right now. You'll see it in 24 hours."),
            ("customer", "Thank you. Why did this happen?"),
            ("agent", "It was a system error on our side. It has been flagged for our engineering team. Again, I sincerely apologize for the inconvenience."),
        ],
    ],
    TicketCategory.GENERAL_INQUIRY.value: [
        [
            ("customer", "What is your return policy?"),
            ("agent", "Great question! Standard members can return items within 30 days of delivery. GOLD and PLATINUM members have 60 days. Items must be in original condition. Non-refundable items include food, beauty products, and digital software."),
            ("customer", "What about electronics?"),
            ("agent", "Electronics are fully refundable within the return window, as long as they're in original packaging with all accessories included."),
            ("customer", "Perfect, thanks!"),
        ],
    ],
}

# Incomplete conversations (customer dropped off mid-session)
INCOMPLETE_ENDINGS = [
    ("customer", "Ok let me check and come back."),
    ("customer", "Hold on, I need to find my order number."),
    ("customer", "One second..."),
]


def generate_conversation(ticket: dict) -> dict:
    category = ticket.get("category", TicketCategory.GENERAL_INQUIRY.value)
    templates = CONVERSATION_TEMPLATES.get(
        category,
        CONVERSATION_TEMPLATES[TicketCategory.GENERAL_INQUIRY.value],
    )
    template = random.choice(templates)

    # Fill in placeholders
    order_id_val = ticket.get("order_id") or "ORD-00000"
    created_dt = datetime.strptime(ticket["created_at"], "%Y-%m-%dT%H:%M:%SZ")

    turns = []
    current_time = created_dt
    for role, message in template:
        message = (
            message
            .replace("{order_id}", order_id_val)
            .replace("{ticket_id}", ticket["ticket_id"])
            .replace("{date}", current_time.strftime("%B %d, %Y"))
            .replace("{amount}", str(round(random.uniform(20, 300), 2)))
            .replace("{product}", "your selected item")
        )
        turns.append({
            "role": role,
            "message": message,
            "timestamp": iso(current_time),
        })
        current_time = datetime_after(current_time, min_hours=0, max_hours=0)
        # Advance by 30 seconds to 3 minutes per message turn
        from datetime import timedelta
        current_time = current_time + timedelta(seconds=random.randint(30, 180))

    # 10% of conversations are incomplete
    is_incomplete = random.choices([True, False], weights=[10, 90])[0]
    if is_incomplete:
        turns.append({
            "role": "customer",
            "message": random.choice(INCOMPLETE_ENDINGS)[1],
            "timestamp": iso(current_time),
        })

    resolved = not is_incomplete and ticket["status"] in ("RESOLVED", "CLOSED")

    return {
        "conversation_id": conversation_id(),
        "ticket_id": ticket["ticket_id"],
        "customer_id": ticket["customer_id"],
        "order_id": ticket.get("order_id"),
        "channel": ticket.get("channel", "CHAT"),
        "is_complete": not is_incomplete,
        "is_resolved": resolved,
        "turn_count": len(turns),
        "turns": turns,
        "started_at": iso(created_dt),
        "ended_at": iso(current_time) if not is_incomplete else None,
    }


def generate_conversations(tickets: list[dict], n: int = 500) -> list[dict]:
    """Generate conversations for a random sample of tickets."""
    sampled = random.sample(tickets, min(n, len(tickets)))
    return [generate_conversation(ticket) for ticket in sampled]
