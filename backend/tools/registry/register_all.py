from backend.tools.customer_tools import lookup_customer, get_customer_tier
from backend.tools.order_tools import get_order, get_orders_by_customer, cancel_order
from backend.tools.refund_tools import initiate_refund, check_refund_status
from backend.tools.shipment_tools import track_shipment, get_shipment_by_order
from backend.tools.ticket_tools import create_ticket, escalate_ticket
from backend.tools.notification_tools import send_notification
from backend.tools.knowledge_base_tools import search_knowledge_base
from backend.tools.payment_tool import get_payment

from backend.tools.registry.registry import tool_registry
from backend.models.tools import ToolPermission


def register_all_tools():
    # --- Customer tools (read-only, broad access) ---
    tool_registry.register(
        "lookup_customer",
        lookup_customer,
        "Look up customer by ID or email",
        ToolPermission(
            allowed_agents=[
                "intent_agent",
                "order_agent",
                "refund_agent",
                "shipping_agent",
            ],
            rate_limit=120,
        ),
        category="customer",
    )
    tool_registry.register(
        "get_customer_tier",
        get_customer_tier,
        "Get customer loyalty tier",
        ToolPermission(
            allowed_agents=["order_agent", "refund_agent"],
            rate_limit=120,
        ),
        category="customer",
    )

    # --- Order tools ---
    tool_registry.register(
        "get_order",
        get_order,
        "Retrieve order details by order ID",
        ToolPermission(
            allowed_agents=["order_agent", "refund_agent", "shipping_agent"],
            rate_limit=100,
        ),
        category="order",
    )
    tool_registry.register(
        "get_orders_by_customer",
        get_orders_by_customer,
        "List all orders for a customer",
        ToolPermission(
            allowed_agents=["order_agent", "refund_agent"],
            rate_limit=60,
        ),
        category="order",
    )
    tool_registry.register(
        "cancel_order",
        cancel_order,
        "Cancel an existing order",
        ToolPermission(
            allowed_agents=["order_agent"],
            is_destructive=True,
            requires_approval=True,
            rate_limit=20,
            cooldown=5,
        ),
        category="order",
    )

    # --- Refund tools ---
    tool_registry.register(
        "initiate_refund",
        initiate_refund,
        "Initiate a refund for an order",
        ToolPermission(
            allowed_agents=["refund_agent"],
            is_destructive=True,
            requires_approval=True,
            rate_limit=20,
            cooldown=5,
        ),
        category="refund",
    )
    tool_registry.register(
        "check_refund_status",
        check_refund_status,
        "Check status of an existing refund",
        ToolPermission(
            allowed_agents=["refund_agent", "order_agent"],
            rate_limit=60,
        ),
        category="refund",
    )

    # --- Shipment tools ---
    tool_registry.register(
        "track_shipment",
        track_shipment,
        "Track a shipment by tracking ID",
        ToolPermission(
            allowed_agents=["shipping_agent"],
            rate_limit=100,
        ),
        category="shipment",
    )
    tool_registry.register(
        "get_shipment_by_order",
        get_shipment_by_order,
        "Get shipment info for an order",
        ToolPermission(
            allowed_agents=["shipping_agent", "order_agent"],
            rate_limit=100,
        ),
        category="shipment",
    )

    # --- Ticket tools ---
    tool_registry.register(
        "create_ticket",
        create_ticket,
        "Create a support ticket",
        ToolPermission(
            allowed_agents=["order_agent", "refund_agent", "shipping_agent"],
            rate_limit=30,
        ),
        category="ticket",
    )
    tool_registry.register(
        "escalate_ticket",
        escalate_ticket,
        "Escalate a ticket to a human agent",
        ToolPermission(
            allowed_agents=["order_agent", "refund_agent", "shipping_agent"],
            requires_approval=True,
            rate_limit=10,
        ),
        category="ticket",
    )

    # --- Notification tools ---
    tool_registry.register(
        "send_notification",
        send_notification,
        "Send notification to customer",
        ToolPermission(
            allowed_agents=["order_agent", "refund_agent", "shipping_agent"],
            rate_limit=30,
        ),
        category="notification",
    )

    # --- Knowledge base ---
    tool_registry.register(
        "search_knowledge_base",
        search_knowledge_base,
        "Search FAQ / policy knowledge base",
        ToolPermission(
            allowed_agents=[
                "intent_agent",
                "order_agent",
                "refund_agent",
                "shipping_agent",
                "response_generator",
            ],
            rate_limit=100,
        ),
        category="knowledge",
    )
    tool_registry.register(
        "get_payment",
        get_payment,
        "Look up order by ID",
        ToolPermission(
            allowed_agents=[
                "order_agent",
                "refund_agent"
            ],
            rate_limit=120,
        ),
        category="payment",
    )
    return tool_registry
