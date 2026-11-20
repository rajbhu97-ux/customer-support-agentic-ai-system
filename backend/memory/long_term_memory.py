from __future__ import annotations
import time
import json
import logging
from typing import Any, Optional

import boto3

logger = logging.getLogger(__name__)


class LongTermMemory:
    def __init__(self, table_name: str, region: str = "ap-south-1"):
        self.table = boto3.resource("dynamodb", region_name=region).Table(table_name)

    def get_customer_context(self, customer_id: str) -> dict[str, Any]:
        resp = self.table.get_item(Key={
            "PK": f"CUSTOMER#{customer_id}",
            "SK": "CONTEXT",
        })
        item = resp.get("Item", {})
        return {
            "customer_id": customer_id,
            "total_interactions": item.get("total_interactions", 0),
            "intents_histogram": json.loads(item.get("intents_histogram", "{}")),
            "last_interaction": item.get("last_interaction", 0),
            "satisfaction_scores": json.loads(item.get("satisfaction_scores", "[]")),
            "notes": json.loads(item.get("notes", "[]")),
            "preferred_channel": item.get("preferred_channel", "chat"),
        }

    def record_interaction(
        self,
        customer_id: str,
        intent: str,
        satisfaction: Optional[float] = None,
        note: Optional[str] = None,
    ):
        now = int(time.time())
        update_expr = (
            "SET total_interactions = if_not_exists(total_interactions, :zero) + :one, "
            "last_interaction = :now"
        )
        attr_values: dict[str, Any] = {":zero": 0, ":one": 1, ":now": now}

        # Increment intent count
        update_expr += ", intents_histogram = if_not_exists(intents_histogram, :empty_map)"
        attr_values[":empty_map"] = "{}"

        self.table.update_item(
            Key={"PK": f"CUSTOMER#{customer_id}", "SK": "CONTEXT"},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=attr_values,
        )

        # Update intent histogram separately (atomic increment not easy in JSON string)
        ctx = self.get_customer_context(customer_id)
        histogram = ctx["intents_histogram"]
        histogram[intent] = histogram.get(intent, 0) + 1

        updates = {"intents_histogram": json.dumps(histogram)}
        if satisfaction is not None:
            scores = ctx["satisfaction_scores"][-19:]  # keep last 20
            scores.append(satisfaction)
            updates["satisfaction_scores"] = json.dumps(scores)
        if note:
            notes = ctx["notes"][-49:]  # keep last 50
            notes.append({"text": note, "ts": now})
            updates["notes"] = json.dumps(notes)

        update_parts = [f"{k} = :{k}" for k in updates]
        self.table.update_item(
            Key={"PK": f"CUSTOMER#{customer_id}", "SK": "CONTEXT"},
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeValues={f":{k}": v for k, v in updates.items()},
        )
        logger.info(f"Recorded interaction for customer {customer_id}, intent={intent}")

    def get_avg_satisfaction(self, customer_id: str) -> Optional[float]:
        ctx = self.get_customer_context(customer_id)
        scores = ctx["satisfaction_scores"]
        return sum(scores) / len(scores) if scores else None

    def add_note(self, customer_id: str, note: str):
        self.record_interaction(customer_id, intent="_note", note=note)