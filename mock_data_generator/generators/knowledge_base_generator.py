"""
Generates synthetic knowledge base articles (FAQ + How-To).

These are the documents the RAG retrieval agent will search.
Each article has a title, body, category, and tags.
The agent must retrieve the right article to answer customer questions.

Deliberately includes some similar-sounding articles to test
retrieval precision (Phase 2 challenge).
"""

from mock_data_generator.utils.faker_helpers import kb_article_id


KB_ARTICLES: list[dict] = [
    # ── Returns & Refunds ─────────────────────────────────────────────────────
    {
        "article_id": kb_article_id(),
        "title": "How to Return an Item",
        "category": "RETURNS",
        "tags": ["return", "refund", "send back", "return label"],
        "body": (
            "To return an item, log in to your account and go to Order History. "
            "Select the order and click 'Return Item'. Choose a reason and confirm. "
            "A prepaid return label will be emailed to you within 30 minutes. "
            "Drop the package at any UPS or FedEx location. "
            "Refunds are processed 5–7 business days after we receive the item."
        ),
    },
    {
        "article_id": kb_article_id(),
        "title": "Return Policy Overview",
        "category": "RETURNS",
        "tags": ["return policy", "30 days", "eligibility", "non-refundable"],
        "body": (
            "Standard members have 30 days from delivery to return eligible items. "
            "GOLD and PLATINUM members have 60 days. "
            "Non-refundable categories include: food, beauty products, digital software, and gift cards. "
            "Items must be unused and in original packaging."
        ),
    },
    {
        "article_id": kb_article_id(),
        "title": "Refund Timeline and Status",
        "category": "REFUNDS",
        "tags": ["refund status", "when will I get my refund", "refund timeline"],
        "body": (
            "Once your return is received, refunds are processed in 5–7 business days for standard members, "
            "and 2–3 business days for GOLD and PLATINUM members. "
            "The refund is sent to your original payment method. "
            "You can check your refund status under Account > Refunds."
        ),
    },
    {
        "article_id": kb_article_id(),
        "title": "I Was Charged But My Order Failed",
        "category": "PAYMENTS",
        "tags": ["charged", "order failed", "payment taken", "money deducted", "ghost payment"],
        "body": (
            "If you were charged but your order shows as failed or cancelled, this is a known issue "
            "called a ghost payment. Your money has not been lost. "
            "We automatically detect this and issue a full refund within 24 hours. "
            "You will receive a confirmation email once the refund is initiated. "
            "If you do not see the refund after 24 hours, please contact support."
        ),
    },
    # ── Shipping & Tracking ───────────────────────────────────────────────────
    {
        "article_id": kb_article_id(),
        "title": "How to Track Your Order",
        "category": "SHIPPING",
        "tags": ["track order", "tracking number", "where is my order", "shipping status"],
        "body": (
            "Once your order ships, you will receive a tracking number by email. "
            "You can also find it under Order History > Your Order > Tracking. "
            "Click the tracking number to go to the carrier's tracking page. "
            "Standard shipping takes 3–5 business days. Express takes 1–2 business days."
        ),
    },
    {
        "article_id": kb_article_id(),
        "title": "My Package Shows Delivered But I Did Not Receive It",
        "category": "SHIPPING",
        "tags": ["delivered", "not received", "missing package", "carrier says delivered"],
        "body": (
            "First, check around your delivery location — packages are sometimes left with neighbors "
            "or in a safe spot. Check your mailbox and building lobby. "
            "If you still cannot find it, wait 24 hours as carriers sometimes mark packages "
            "delivered slightly early. "
            "If after 24 hours the package is still missing, contact us and we will investigate "
            "with the carrier and arrange a reship or refund."
        ),
    },
    {
        "article_id": kb_article_id(),
        "title": "Shipping Delays and Estimated Delivery",
        "category": "SHIPPING",
        "tags": ["delayed", "late delivery", "estimated delivery", "shipping time"],
        "body": (
            "Delivery estimates are not guaranteed. Delays can occur due to weather, "
            "high order volume, or carrier issues. "
            "If your package is more than 3 days past the estimated delivery date, "
            "contact us and we will investigate. "
            "PLATINUM members get priority re-routing in case of delays."
        ),
    },
    # ── Orders ────────────────────────────────────────────────────────────────
    {
        "article_id": kb_article_id(),
        "title": "How to Cancel an Order",
        "category": "ORDERS",
        "tags": ["cancel order", "cancellation", "stop order"],
        "body": (
            "Orders can be cancelled within 1 hour of placement if they have not entered processing. "
            "Go to Order History and click 'Cancel Order'. "
            "If the order is already processing or shipped, you cannot cancel it online — "
            "contact support immediately and we will attempt to intercept the shipment."
        ),
    },
    {
        "article_id": kb_article_id(),
        "title": "Wrong Item Delivered",
        "category": "ORDERS",
        "tags": ["wrong item", "incorrect item", "received wrong product"],
        "body": (
            "We apologize for sending the wrong item. "
            "Please do not return the item until we confirm. "
            "Contact support with your order ID and a photo of the received item. "
            "We will ship the correct item at no extra charge and provide a free return label "
            "for the wrong item."
        ),
    },
    # ── Payments ──────────────────────────────────────────────────────────────
    {
        "article_id": kb_article_id(),
        "title": "Accepted Payment Methods",
        "category": "PAYMENTS",
        "tags": ["payment methods", "credit card", "paypal", "apple pay"],
        "body": (
            "We accept Visa, Mastercard, American Express, Discover, PayPal, Apple Pay, and Google Pay. "
            "We do not accept cash, checks, or cryptocurrency."
        ),
    },
    {
        "article_id": kb_article_id(),
        "title": "Double Charge on My Account",
        "category": "PAYMENTS",
        "tags": ["double charge", "charged twice", "duplicate payment"],
        "body": (
            "Sometimes a pending authorization can look like a double charge but is not. "
            "Wait 24 hours to see if the duplicate charge disappears. "
            "If after 24 hours you still see two charges for the same order, "
            "contact support with your order ID and we will investigate and refund the duplicate."
        ),
    },
    # ── Account ───────────────────────────────────────────────────────────────
    {
        "article_id": kb_article_id(),
        "title": "How to Reset Your Password",
        "category": "ACCOUNT",
        "tags": ["password", "reset password", "forgot password", "login"],
        "body": (
            "Click 'Forgot Password' on the login page and enter your email address. "
            "You will receive a reset link within 5 minutes. "
            "The link expires after 30 minutes. "
            "If you do not receive the email, check your spam folder."
        ),
    },
    {
        "article_id": kb_article_id(),
        "title": "Member Tier Benefits",
        "category": "ACCOUNT",
        "tags": ["tier", "gold", "platinum", "silver", "benefits", "membership"],
        "body": (
            "STANDARD: 30-day returns, standard support. "
            "SILVER: 30-day returns, priority email support. "
            "GOLD: 60-day returns, $200 auto-refund limit, priority phone support. "
            "PLATINUM: 60-day returns, $500 auto-refund limit, free return shipping, "
            "dedicated agent, 30-minute response SLA."
        ),
    },
]


def generate_knowledge_base() -> list[dict]:
    """Knowledge base articles are static — return the pre-defined list."""
    return KB_ARTICLES
