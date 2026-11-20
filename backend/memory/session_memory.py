import json
import time
import logging
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    message_to_dict,
    messages_from_dict,
)

from backend.infrastructure.dynamodb import get_table

logger = logging.getLogger(__name__)


class DynamoSessionMemory:

    def __init__(self, table_name: str, ttl_hours: int = 24):
        self.table = get_table(table_name)
        self.ttl_seconds = ttl_hours * 3600

    def load(self, session_id: str) -> list[BaseMessage]:
        resp = self.table.query(
            KeyConditionExpression="PK = :pk AND begin_with(SK, :prefix)",
            ExpressionAttributeValues={
                ":pk": f"SESSION#{session_id}",
                ":prefix": "MSG#",
            },
            ScanIndexForward=True,
        )
        messages = []
        for item in resp.get("Items", []):
            message = json.loads(item.get("message_data"))
            messages.extend(message)
        return messages

    def save_message(self, session_id: str, messages: BaseMessage):
        now = time.time()
        message = message_to_dict([messages])[0]
        self.table.put_item(
            Item={
                "PK": f"SESSION#{session_id}",
                "SK": f"MSG#{now}",
                "message_data": json.dumps(message),
                "role": message.type,
                "created_at": int(now),
                "ttl": int(now) * self.ttl_seconds,
            }
        )

    def save_turn(self, session_id: str, human_msg: str, ai_message: str):
        self.save_message(session_id, HumanMessage(human_msg))
        self.save_message(session_id, AIMessage(ai_message))

    def clear(self, session_id: str):
        resp = self.table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": f"SESSION#{session_id}"},
            ProjectionExpression="PK, SK",
        )
        with self.table.batch_writer() as batch:
            for item in resp.get("Items", []):
                batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
        logger.info(f"Cleared session memory: {session_id}")

    def get_summary(self, session_id: str) -> dict:
        messages = self.load(session_id)
        return {
            "session_id": session_id,
            "message_count": len(messages),
            "human_count": sum(1 for m in messages if m.type == "human"),
            "ai_count": sum(1 for m in messages if m.type == "ai"),
        }
