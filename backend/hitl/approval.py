import boto3
from typing import Any
import time
import uuid
import logging
import json
from botocore.exceptions import ClientError

from backend.infrastructure.dynamodb import get_table
from backend.hitl.model import ApprovalRequest
from backend.models.enums import ApprovalStatus

logger = logging.getLogger(__name__)


class ApprovalRequest:
    request_id: str
    session_id: str
    tool_name: str
    agent_id: str
    parameter: dict[str, Any]
    reason: str
    status: str = ApprovalStatus.PENDING
    created_at: float = 0.0
    resolved_at: float = 0.0
    resolved_by: str = ""
    ttl: int = 0


class ApprovalManager:

    def __init__(self, table_name: str, sns_topic_arn: str, region: str = "us-east-1"):
        self.table = get_table(table_name)
        self.sns = boto3.client("sns", region_name="us-east-1")
        self.sns_topic_arn = sns_topic_arn
        self.ttl = 3600

    async def request_approval(
        self,
        session_id: str,
        tool_name: str,
        agent_id: str,
        parameter: dict[str, Any],
        reason: str,
    ) -> ApprovalRequest:
        now = time.time()
        approval_request = ApprovalRequest(
            request_id=str(uuid.uuid4()),
            session_id=session_id,
            tool_name=tool_name,
            agent_id=agent_id,
            parameter=json.dumps(parameter),
            reason=reason,
            status=ApprovalStatus.PENDING,
            created_at=now,
            ttl=int(now) + self.ttl,
        )
        self.table.put_item(
            Item={
                "PK": f"APPROVAL#{request_id}",
                "SK": f"SESSION#{session_id}",
                "request_id": request_id,
                "session_id": session_id,
                "tool_name": tool_name,
                "agent_id": agent_id,
                "parameter": parameter,
                "reason": reason,
                "status": "PENDING",
                "created_at": now,
                "ttl": approval_request.ttl,
            }
        )

    def _notify_agent(self, req: ApprovalRequest):
        try:
            self.sns.publish(
                TopicArn=self.sns_topic_arn,
                Message=f"Approval required for {req.tool_name}",
                Subject=json.dumps(
                    {
                        "request_id": req.request_id,
                        "session_id": req.session_id,
                        "agent_id": req.agent_id,
                        "parameter": req.parameter,
                    }
                ),
                MessageAttributes={
                    "event_type": {
                        "DataType": "String",
                        "StringValue": "APPROVAL_REQUIRED",
                    },
                },
            )
        except ClientError as e:
            logger.error(f"SNS publish failed: {e}")

    def approve(self, request_id: str, resolved_by: str):
        return _approve(request_id, ApprovalStatus.APPROVE, resolved_by)

    def reject(self, request_id: str, resolved_by: str):
        return _approve(request_id, ApprovalStatus.REJECTED, resolved_by)

    def _approve(
        self, request_id: str, status: ApprovalStatus, resolved_by: str
    ) -> bool:
        now = time.time()
        try:
            self.table.update_item(
                Key={"PK": f"APPROVAL#{request_id}"},
                UpdateExpression="SET #s = :s, resolved_at = :t, resolved_by = :r",
                ConditionExpression="#s = :pending",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":s": status.value,
                    ":t": now,
                    ":r": resolved_by,
                    ":pending": ApprovalStatus.PENDING.value,
                },
            )
            logger.info(f"Approval {request_id} -> {status} by {resolved_by}")
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.warning(
                    f"Approval request {request_id} already approved/rejected"
                )
            return False

    def get_status(self, request_id: str):
        item = self.table.get_item(Key={"PK": f"APPROVAL#{request_id}"})
        return item.get("Item")

    def get_pending_for_session(self, session_id: str) -> list[dict]:
        resp = self.table.query(
            IndexName="GSI-SessionApprovals",
            KeyConditionExpression="session_id = :sid AND #s = :pending",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":sid": session_id,
                ":pending": ApprovalStatus.PENDING.value,
            },
        )
        return resp.get("Items", [])
