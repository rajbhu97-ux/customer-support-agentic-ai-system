from typing import Any
from dataclasses import dataclass


@dataclass
class ApprovalRequest:
    request_id: str
    session_id: str
    tool_name: str
    agent_id: str
    parameter: dict[str, Any]
    reason: str
    status: str = "PENDING"
    created_at: float = 0.0
    resolved_at: float = 0.0
    resolved_by: str = ""
    ttl: int = 0
