from langgraph.graph import StateGraph, START, END
from backend.models.agent_state import State
from backend.graph.nodes.input_validation_node import input_validation_node
from backend.graph.nodes.intent_agent_node import intent_agent_node
from backend.graph.nodes.order_agent_node import order_agent_node
from backend.graph.nodes.refund_agent_node import refund_agent_node
from backend.graph.nodes.terminal_nodes import rejection_node, human_review_node
from backend.graph.nodes.response_generator_agent_node import (
    response_generator_agent_node,
)
from backend.graph.nodes.shipping_agent_node import shipping_agent_node
from backend.graph.nodes.output_validation_node import (
    validate_intent_output,
    validate_domain_output,
    validate_response_output,
)
from backend.graph.routing.input_router import route_after_input_validation
from backend.graph.routing.intent_router import route_after_intent_agent
from backend.graph.routing.error_router import route_after_node, route_error_handler


def build_graph():
    graph = StateGraph(State)

    graph.add_node("input_validation", input_validation_node)
    graph.add_node("intent_agent", intent_agent_node)
    graph.add_node("validate_intent", validate_intent_output)
    graph.add_node("order_agent", order_agent_node)
    graph.add_node("refund_agent", refund_agent_node)
    graph.add_node("shipping_agent", shipping_agent_node)
    graph.add_node("validate_domain", validate_domain_output)
    graph.add_node("response_generator", response_generator_agent_node)
    graph.add_node("validate_response", validate_response_output)

    graph.add_node("human_approval", human_review_node)
    graph.add_node("rejection", rejection_node)

    graph.add_edge(START, "input_validation")

    graph.add_conditional_edges(
        "input_validation",
        route_after_input_validation,
        {
            "continue": "intent_agent",
            "reject": "rejection",
            "human_review": "human_approval",
        },
    )
    graph.add_conditional_edges(
        "intent_agent",
        route_after_node,
        {
            "continue": "validate_intent",
            "retry": "intent_agent",
            "fallback": END,
            "reject": "rejection",
            "human_review": "human_approval",
        },
    )

    graph.add_conditional_edges(
        "validate_intent",
        route_after_intent_agent,
        {
            "order_agent": "order_agent",
            "shipping_agent": "shipping_agent",
            "refund_agent": "refund_agent",
            "retry": "intent_agent",
            "fallback": END,
            "reject": "rejection",
            "human_review": "human_approval",
        },
    )

    for agent in ["order_agent", "shipping_agent", "refund_agent"]:
        graph.add_conditional_edges(
            agent,
            route_after_node,
            {
                "continue": "validate_domain",
                "retry": agent,
                "fallback": END,
                "reject": "rejection",
                "human_review": "human_approval",
            },
        )

    graph.add_conditional_edges(
        "validate_domain",
        route_after_node,
        {
            "continue": "response_generator",
            "error": "error_handler",
            "human_review": "human_review",
            "retry": "error_handler",
            "fallback": END,
        },
    )

    graph.add_conditional_edges(
        "response_generator",
        route_after_node,
        {
            "continue": "validate_response",
            "error": "error_handler",
            "human_review": "human_review",
            "retry": "response_generator",
            "fallback": END,
        },
    )

    graph.add_conditional_edges(
        "validate_response",
        route_after_node,
        {
            "continue": END,
            "error": "error_handler",
            "human_review": "human_review",
            "retry": "response_generator",
            "fallback": END,
        },
    )

    graph.add_conditional_edges(
        "error_handler",
        route_error_handler,
        {
            "reject": "rejection",
            "human_review": "human_review",
        },
    )

    graph.add_edge("rejection", END)
    graph.add_edge("human_review", END)

    return graph


app_graph = build_graph().compile()
