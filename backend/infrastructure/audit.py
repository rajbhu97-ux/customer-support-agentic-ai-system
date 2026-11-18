from backend.infrastructure.dynamodb import get_table
from datetime import datetime, timedelta
import json

class AuditLogger:
    def __init__(self):
        self.table = get_table("AgentAuditLog")

    def log_agent_action(
        self,
        session_id: str,
        agent_name: str,
        action: str,
        input_data: dict,
        output_data: dict,
        latency_ms: float,
        user_id: str = None,
    ):
        ttl = int((datetime.utcnow() + timedelta(days=90)).timestamp())
        self.table.put_item(Item={
            "PK": f"SESSION#{session_id}",
            "SK": f"EVENT#{datetime.utcnow().isoformat()}",
            "agent_name": agent_name,
            "action": action,
            "input_summary": json.dumps(input_data)[:1000],
            "output_summary": json.dumps(output_data)[:1000],
            "latency_ms": int(latency_ms),
            "user_id": user_id,
            "ttl": ttl,
        })

audit = AuditLogger()