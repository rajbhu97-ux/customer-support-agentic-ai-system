from .base import BaseLLMProvider
from langchain_core.language_models.fake_chat_models import FakeListChatModel
import json

class MockProvider(BaseLLMProvider):

    DEFAULT_RESPONSES: list[str] = [json.dumps(ele) for ele in [{"intent": "ORDER_STATUS", "confidence": 0.95, "urgency": "MEDIUM", "sentiment": "NEUTRAL", "entities": {"order_id": "ORD-12345",
  "product_name": None, "amount": None, "date": None}, "summary": "Customer wants to know the status of order ORD-12345"},{"status": "resolved", "actions_taken": [{"tool": "lookup_order", "result": "Order ORD-12345 found, status is shipped"}, {"tool":
  "lookup_shipment", "result": "Package in transit, expected delivery tomorrow"}], "resolution_summary": "Order ORD-12345 is shipped and arriving tomorrow", "data_for_response": {"order_id": "ORD-12345", "order_status": "shipped", "action_taken": "info_provided",
  "ticket_id": None, "additional_info": "Expected delivery October 16"}, "escalation_reason": None} ]] + ["Your order ORD-12345 is on its way! It's currently in transit and expected to arrive tomorrow. If you have any other questions,I'm happy to help"]

    @property
    def provider_name(self) -> str:
        return "mock"

    def validate_config(self) -> None:
        pass

    def get_llm(self, temperature=0.0):
        return FakeListChatModel(
            responses=self.DEFAULT_RESPONSES,
            temperature=temperature
        )
