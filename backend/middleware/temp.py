
# backend/hitl/approval.py
from __future__ import annotations
import uuid
import time
import json
import logging
from dataclasses import dataclass, asdict
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


@dataclass
class ApprovalRequest:
    request_id: str
    session_id: str
    tool_name: str
    agent_id: str
    parameters: dict[str, Any]
    reason: str
    status: str = "PENDING"          # PENDING | APPROVED | REJECTED | EXPIRED
    created_at: float = 0.0
    resolved_at: float = 0.0
    resolved_by: str = ""
    ttl: int = 0


class ApprovalManager:
    def __init__(self, table_name: str, sns_topic_arn: str, region: str = "ap-south-1"):
        self.dynamo = boto3.resource("dynamodb", region_name=region)
        self.table = self.dynamo.Table(table_name)
        self.sns = boto3.client("sns", region_name=region)
        self.sns_topic_arn = sns_topic_arn
        self.ttl_seconds = 3600  # 1 hour expiry

    async def request_approval(
        self,
        session_id: str,
        tool_name: str,
        agent_id: str,
        parameters: dict[str, Any],
        reason: str,
    ) -> ApprovalRequest:
        now = time.time()
        req = ApprovalRequest(
            request_id=str(uuid.uuid4()),
            session_id=session_id,
            tool_name=tool_name,
            agent_id=agent_id,
            parameters=parameters,
            reason=reason,
            created_at=now,
            ttl=int(now) + self.ttl_seconds,
        )
        self.table.put_item(Item={
            "PK": f"APPROVAL#{req.request_id}",
            "SK": f"SESSION#{session_id}",
            "request_id": req.request_id,
            "session_id": session_id,
            "tool_name": tool_name,
            "agent_id": agent_id,
            "parameters": json.dumps(parameters),
            "reason": reason,
            "status": "PENDING",
            "created_at": int(now),
            "ttl": req.ttl,
        })
        self._notify_agent(req)
        logger.info(f"Approval requested: {req.request_id} for {tool_name}")
        return req

    def _notify_agent(self, req: ApprovalRequest):
        try:
            self.sns.publish(
                TopicArn=self.sns_topic_arn,
                Subject=f"Approval Required: {req.tool_name}",
                Message=json.dumps({
                    "request_id": req.request_id,
                    "session_id": req.session_id,
                    "tool_name": req.tool_name,
                    "agent_id": req.agent_id,
                    "reason": req.reason,
                    "parameters": req.parameters,
                }),
                MessageAttributes={
                    "event_type": {"DataType": "String", "StringValue": "APPROVAL_REQUIRED"},
                },
            )
        except ClientError as e:
            logger.error(f"SNS publish failed: {e}")

    def approve(self, request_id: str, resolved_by: str) -> bool:
        return self._resolve(request_id, "APPROVED", resolved_by)

    def reject(self, request_id: str, resolved_by: str) -> bool:
        return self._resolve(request_id, "REJECTED", resolved_by)

    def _resolve(self, request_id: str, status: str, resolved_by: str) -> bool:
        try:
            self.table.update_item(
                Key={"PK": f"APPROVAL#{request_id}"},
                UpdateExpression="SET #s = :s, resolved_at = :t, resolved_by = :r",
                ConditionExpression="#s = :pending",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":s": status,
                    ":t": int(time.time()),
                    ":r": resolved_by,
                    ":pending": "PENDING",
                },
            )
            logger.info(f"Approval {request_id} -> {status} by {resolved_by}")
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.warning(f"Approval {request_id} already resolved or expired")
            return False

    def get_status(self, request_id: str) -> Optional[dict]:
        resp = self.table.get_item(Key={"PK": f"APPROVAL#{request_id}"})
        return resp.get("Item")

    def get_pending_for_session(self, session_id: str) -> list[dict]:
        resp = self.table.query(
            IndexName="GSI-SessionApprovals",
            KeyConditionExpression="session_id = :sid AND #s = :pending",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":sid": session_id, ":pending": "PENDING"},
        )
        return resp.get("Items", [])


# backend/hitl/routes.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.hitl.approval import ApprovalManager
from config.settings import settings

router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])


def get_approval_manager() -> ApprovalManager:
    return ApprovalManager(
        table_name=settings.dynamodb_table_name,
        sns_topic_arn=settings.sns_approval_topic_arn,
        region=settings.aws_region,
    )


class ResolveRequest(BaseModel):
    resolved_by: str


@router.get("/{request_id}")
async def get_approval(request_id: str, mgr: ApprovalManager = Depends(get_approval_manager)):
    item = mgr.get_status(request_id)
    if not item:
        raise HTTPException(404, "Approval request not found")
    return item


@router.post("/{request_id}/approve")
async def approve(request_id: str, body: ResolveRequest, mgr: ApprovalManager = Depends(get_approval_manager)):
    if not mgr.approve(request_id, body.resolved_by):
        raise HTTPException(409, "Already resolved or expired")
    return {"status": "APPROVED"}


@router.post("/{request_id}/reject")
async def reject(request_id: str, body: ResolveRequest, mgr: ApprovalManager = Depends(get_approval_manager)):
    if not mgr.reject(request_id, body.resolved_by):
        raise HTTPException(409, "Already resolved or expired")
    return {"status": "REJECTED"}


@router.get("/session/{session_id}/pending")
async def pending_for_session(session_id: str, mgr: ApprovalManager = Depends(get_approval_manager)):
    return mgr.get_pending_for_session(session_id)



# backend/memory/session_memory.py
from __future__ import annotations
import time
import json
import logging
from typing import Any

import boto3
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, messages_to_dict, messages_from_dict

logger = logging.getLogger(__name__)


class DynamoSessionMemory:
    def __init__(self, table_name: str, region: str = "ap-south-1", ttl_hours: int = 24):
        self.table = boto3.resource("dynamodb", region_name=region).Table(table_name)
        self.ttl_seconds = ttl_hours * 3600

    def load(self, session_id: str) -> list[BaseMessage]:
        resp = self.table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
            ExpressionAttributeValues={
                ":pk": f"SESSION#{session_id}",
                ":prefix": "MSG#",
            },
            ScanIndexForward=True,
        )
        messages = []
        for item in resp.get("Items", []):
            msg_data = json.loads(item["message_data"])
            messages.extend(messages_from_dict([msg_data]))
        return messages

    def save_message(self, session_id: str, message: BaseMessage):
        now = time.time()
        msg_dict = messages_to_dict([message])[0]
        self.table.put_item(Item={
            "PK": f"SESSION#{session_id}",
            "SK": f"MSG#{int(now * 1000)}",
            "message_data": json.dumps(msg_dict),
            "role": message.type,
            "created_at": int(now),
            "ttl": int(now) + self.ttl_seconds,
        })

    def save_turn(self, session_id: str, human_msg: str, ai_msg: str):
        self.save_message(session_id, HumanMessage(content=human_msg))
        self.save_message(session_id, AIMessage(content=ai_msg))

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

# backend/memory/long_term_memory.py
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


# backend/api/chat_routes.py
from __future__ import annotations
import uuid
import json
import logging
import asyncio
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from pydantic import BaseModel

from backend.graph.graph import build_graph
from backend.memory.session_memory import DynamoSessionMemory
from backend.memory.long_term_memory import LongTermMemory
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Lazy-init singletons
_graph = None
_session_memory = None
_ltm = None


def _get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def _get_session_memory() -> DynamoSessionMemory:
    global _session_memory
    if _session_memory is None:
        _session_memory = DynamoSessionMemory(
            table_name=settings.dynamodb_table_name,
            region=settings.aws_region,
        )
    return _session_memory


def _get_ltm() -> LongTermMemory:
    global _ltm
    if _ltm is None:
        _ltm = LongTermMemory(
            table_name=settings.dynamodb_table_name,
            region=settings.aws_region,
        )
    return _ltm


# ── REST ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    customer_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    intent: Optional[str] = None
    requires_approval: bool = False
    approval_id: Optional[str] = None


@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    graph = _get_graph()
    mem = _get_session_memory()

    history = mem.load(session_id)

    state = {
        "user_message": req.message,
        "session_id": session_id,
        "customer_id": req.customer_id,
        "chat_history": history,
    }

    result = await graph.ainvoke(state)

    final = result.get("final_response", "I'm sorry, I couldn't process your request.")
    intent = result.get("intent_classification", {}).get("intent")
    approval_id = result.get("pending_approval_id")

    mem.save_turn(session_id, req.message, final)

    if req.customer_id and intent:
        _get_ltm().record_interaction(req.customer_id, intent)

    return ChatResponse(
        session_id=session_id,
        response=final,
        intent=intent,
        requires_approval=approval_id is not None,
        approval_id=approval_id,
    )


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    mem = _get_session_memory()
    messages = mem.load(session_id)
    return {
        "session_id": session_id,
        "messages": [{"role": m.type, "content": m.content} for m in messages],
    }


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    _get_session_memory().clear(session_id)
    return {"status": "cleared"}


# ── WebSocket with streaming ─────────────────────────

@router.websocket("/ws/{session_id}")
async def websocket_chat(ws: WebSocket, session_id: str):
    await ws.accept()
    graph = _get_graph()
    mem = _get_session_memory()

    try:
        while True:
            data = await ws.receive_text()
            payload = json.loads(data)
            message = payload.get("message", "")
            customer_id = payload.get("customer_id")

            history = mem.load(session_id)
            state = {
                "user_message": message,
                "session_id": session_id,
                "customer_id": customer_id,
                "chat_history": history,
            }

            # Stream node-by-node
            full_response = ""
            async for event in graph.astream(state, stream_mode="updates"):
                for node_name, node_output in event.items():
                    await ws.send_text(json.dumps({
                        "type": "node_update",
                        "node": node_name,
                        "data": _safe_serialize(node_output),
                    }))
                    if "final_response" in node_output:
                        full_response = node_output["final_response"]

            await ws.send_text(json.dumps({
                "type": "final",
                "response": full_response or "I couldn't process your request.",
                "session_id": session_id,
            }))

            if full_response:
                mem.save_turn(session_id, message, full_response)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await ws.close(code=1011)


def _safe_serialize(obj) -> dict:
    """Best-effort serialize node output for WS."""
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            try:
                json.dumps(v)
                result[k] = v
            except (TypeError, ValueError):
                result[k] = str(v)
        return result
    return {"value": str(obj)}



# config/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # ── General ──
    app_name: str = "customer-support-agentic-ai"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # ── AWS Core ──
    aws_region: str = "ap-south-1"
    aws_account_id: str = ""

    # ── DynamoDB ──
    dynamodb_table_name: str = "customer-support-table"
    dynamodb_endpoint: Optional[str] = None  # for local dev

    # ── Cognito ──
    cognito_user_pool_id: str = ""
    cognito_app_client_id: str = ""
    cognito_domain: str = ""

    # ── Bedrock LLM ──
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    bedrock_max_tokens: int = 2048
    bedrock_temperature: float = 0.3
    bedrock_endpoint: Optional[str] = None

    # ── OpenSearch (RAG) ──
    opensearch_endpoint: str = ""
    opensearch_index: str = "knowledge-base"
    opensearch_collection_name: str = "customer-support-kb"

    # ── Embeddings ──
    embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    embedding_dimension: int = 1024

    # ── SQS ──
    sqs_refund_queue_url: str = ""
    sqs_escalation_queue_url: str = ""
    sqs_notification_queue_url: str = ""

    # ── SNS ──
    sns_customer_topic_arn: str = ""
    sns_agent_topic_arn: str = ""
    sns_approval_topic_arn: str = ""

    # ── S3 ──
    s3_data_bucket: str = ""
    s3_logs_bucket: str = ""

    # ── Secrets Manager ──
    secrets_prefix: str = "customer-support"

    # ── Memory ──
    session_ttl_hours: int = 24
    max_history_messages: int = 20

    # ── Agent Config ──
    agent_max_iterations: int = 5
    agent_timeout_seconds: int = 30

    # ── Resilience ──
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 30
    retry_max_attempts: int = 3
    bulkhead_max_concurrent: int = 10

    # ── API ──
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:8501"]

    # ── Observability ──
    cloudwatch_log_group: str = "/customer-support/app"
    xray_enabled: bool = True
    metrics_namespace: str = "CustomerSupportAI"

    # ── Local Dev ──
    use_local_aws:
