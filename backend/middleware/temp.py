# backend/api/middleware/auth.py
import jwt
import requests
from functools import lru_cache
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.settings import settings

security = HTTPBearer()

@lru_cache()
def get_cognito_jwks():
    url = f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    return requests.get(url).json()

def decode_token(token: str) -> dict:
    jwks = get_cognito_jwks()
    headers = jwt.get_unverified_header(token)
    kid = headers["kid"]

    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if not key:
        raise HTTPException(status_code=401, detail="Invalid token key")

    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)

    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience=settings.COGNITO_CLIENT_ID,
        issuer=f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}"
    )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    try:
        payload = decode_token(credentials.credentials)
        return {
            "user_id": payload["sub"],
            "email": payload.get("email"),
            "groups": payload.get("cognito:groups", []),
            "role": _resolve_role(payload.get("cognito:groups", []))
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def _resolve_role(groups: list[str]) -> str:
    if "admins" in groups:
        return "admin"
    if "agents" in groups:
        return "agent"
    return "customer"





# backend/api/middleware/authorization.py
from functools import wraps
from fastapi import HTTPException

class RequireRole:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: dict):
        if user.get("role") not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user.get('role')}' not authorized. Required: {self.allowed_roles}"
            )
        return user

# Usage in routes:
require_admin = RequireRole(["admin"])
require_agent = RequireRole(["admin", "agent"])
require_customer = RequireRole(["admin", "agent", "customer"])



# backend/api/routes/chat.py
from fastapi import APIRouter, Depends
from backend.api.middleware.auth import get_current_user
from backend.api.middleware.authorization import require_customer

router = APIRouter()

@router.post("/chat")
async def chat(
    request: ChatRequest,
    user: dict = Depends(get_current_user)
):
    # user is authenticated, has user_id, email, role
    require_customer(user)

    initial_state = {
        "raw_user_message": request.message,
        "session_id": request.session_id or str(uuid.uuid4()),
        "user_id": user["user_id"],  # track who's chatting
        "user_role": user["role"],
        "conversation_history": [],
    }
    result = app_graph.invoke(initial_state)
    return ChatResponse(response=result.get("final_response", ""))


@router.get("/tickets")
async def list_tickets(user: dict = Depends(get_current_user)):
    require_agent(user)  # only agents/admins can list all tickets
    # ...

@router.post("/admin/reload-kb")
async def reload_knowledge_base(user: dict = Depends(get_current_user)):
    require_admin(user)
    # ...




# backend/llm/providers/bedrock.py
from .base import BaseLLMProvider
from langchain_aws import ChatBedrock
from langchain_core.language_models import BaseChatModel
from config.settings import settings

class BedrockProvider(BaseLLMProvider):

    def __init__(self):
        self._llm_cache: dict[float, BaseChatModel] = {}
        self.validate_config()

    @property
    def provider_name(self) -> str:
        return "bedrock"

    def validate_config(self) -> None:
        if not settings.AWS_REGION:
            raise ValueError("AWS_REGION is required for Bedrock")

    def get_llm(self, temperature: float = 0.0) -> BaseChatModel:
        if temperature in self._llm_cache:
            return self._llm_cache[temperature]

        model = ChatBedrock(
            model_id=settings.BEDROCK_MODEL_ID,  # "anthropic.claude-3-sonnet-20240229-v1:0"
            region_name=settings.AWS_REGION,
            model_kwargs={
                "temperature": temperature,
                "max_tokens": 2048,
            },
            credentials_profile_name=settings.AWS_PROFILE,  # optional
        )
        self._llm_cache[temperature] = model
        return model



# backend/llm/client.py — add to PROVIDER_REGISTRY
from .providers.bedrock import BedrockProvider

PROVIDER_REGISTRY = {
    "google": GoogleProvider,
    "bedrock": BedrockProvider,
    "mock": MockProvider,
}
# config/settings.py — add
BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
AWS_REGION: str = "ap-south-1"
AWS_PROFILE: Optional[str] = None
LLM_PROVIDER: str = "bedrock"  # change default

# backend/rag/vector_store.py
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
from config.settings import settings

def get_opensearch_client():
    credentials = boto3.Session().get_credentials()
    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        settings.AWS_REGION,
        "aoss",
        session_token=credentials.token,
    )
    return OpenSearch(
        hosts=[{"host": settings.OPENSEARCH_ENDPOINT, "port": 443}],
        http_auth=auth,
        use_ssl=True,
        connection_class=RequestsHttpConnection,
    )


class VectorStore:
    def __init__(self):
        self.client = get_opensearch_client()
        self.index_name = "knowledge-base"

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[dict]:
        body = {
            "size": top_k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": top_k
                    }
                }
            }
        }
        resp = self.client.search(index=self.index_name, body=body)
        return [hit["_source"] for hit in resp["hits"]["hits"]]

    def index_document(self, doc_id: str, content: str, embedding: list[float], metadata: dict):
        self.client.index(
            index=self.index_name,
            id=doc_id,
            body={
                "content": content,
                "embedding": embedding,
                "metadata": metadata,
            }
        )

# backend/rag/embeddings.py
import boto3
import json
from config.settings import settings

bedrock_runtime = boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)

def get_embedding(text: str) -> list[float]:
    response = bedrock_runtime.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text})
    )
    result = json.loads(response["body"].read())
    return result["embedding"]


# backend/infrastructure/sqs.py
import boto3
import json
from config.settings import settings

sqs = boto3.client("sqs", region_name=settings.AWS_REGION)

QUEUES = {
    "refund_processing": settings.SQS_REFUND_QUEUE_URL,
    "ticket_escalation": settings.SQS_ESCALATION_QUEUE_URL,
    "notification": settings.SQS_NOTIFICATION_QUEUE_URL,
}

def send_message(queue_name: str, message: dict, delay_seconds: int = 0):
    sqs.send_message(
        QueueUrl=QUEUES[queue_name],
        MessageBody=json.dumps(message),
        DelaySeconds=delay_seconds,
    )

def send_refund_request(order_id: str, amount: float, customer_id: str):
    send_message("refund_processing", {
        "action": "process_refund",
        "order_id": order_id,
        "amount": amount,
        "customer_id": customer_id,
    })

def send_escalation(ticket_id: str, reason: str, priority: str):
    send_message("ticket_escalation", {
        "action": "escalate",
        "ticket_id": ticket_id,
        "reason": reason,
        "priority": priority,
    })
# backend/infrastructure/sns.py
import boto3
from config.settings import settings

sns = boto3.client("sns", region_name=settings.AWS_REGION)

def send_customer_notification(customer_email: str, subject: str, message: str):
    sns.publish(
        TopicArn=settings.SNS_CUSTOMER_TOPIC_ARN,
        Subject=subject,
        Message=message,
        MessageAttributes={
            "email": {"DataType": "String", "StringValue": customer_email}
        }
    )

def send_agent_alert(message: str, priority: str = "MEDIUM"):
    sns.publish(
        TopicArn=settings.SNS_AGENT_ALERT_TOPIC_ARN,
        Subject=f"[{priority}] Agent Alert",
        Message=message,
    )
# backend/infrastructure/secrets.py
import boto3
import json
from functools import lru_cache
from config.settings import settings

secrets_client = boto3.client("secretsmanager", region_name=settings.AWS_REGION)

@lru_cache()
def get_secret(secret_name: str) -> dict:
    response = secrets_client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

def get_api_keys() -> dict:
    return get_secret("customer-support/api-keys")

def get_db_credentials() -> dict:
    return get_secret("customer-support/db-credentials")
# observability/logger.py
import logging
import json
import watchtower
import boto3
from config.settings import settings

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # CloudWatch handler
    cw_handler = watchtower.CloudWatchLogHandler(
        log_group_name=f"/customer-support/{settings.ENVIRONMENT}",
        stream_name=name,
        boto3_client=boto3.client("logs", region_name=settings.AWS_REGION),
    )
    cw_handler.setFormatter(logging.Formatter(
        json.dumps({
            "timestamp": "%(asctime)s",
            "level": "%(levelname)s",
            "logger": "%(name)s",
            "message": "%(message)s",
        })
    ))
    logger.addHandler(cw_handler)

    # Console handler for local dev
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(console)

    return logger


# observability/metrics.py
import boto3
from config.settings import settings

cloudwatch = boto3.client("cloudwatch", region_name=settings.AWS_REGION)

def put_metric(metric_name: str, value: float, unit: str = "Count", dimensions: dict = None):
    dim_list = [{"Name": k, "Value": v} for k, v in (dimensions or {}).items()]
    cloudwatch.put_metric_data(
        Namespace="CustomerSupport",
        MetricData=[{
            "MetricName": metric_name,
            "Value": value,
            "Unit": unit,
            "Dimensions": dim_list,
        }]
    )

# Usage in agents:
# put_metric("IntentClassified", 1, dimensions={"intent": "ORDER_STATUS"})
# put_metric("AgentLatency", 1.5, unit="Seconds", dimensions={"agent": "order_agent"})
# put_metric("RefundProcessed", 49.99, unit="None", dimensions={"tier": "GOLD"})


# observability/tracer.py
from aws_xray_sdk.core import xray_recorder, patch_all
from config.settings import settings

def setup_tracing():
    if settings.ENABLE_TRACING:
        xray_recorder.configure(
            service="customer-support-ai",
            sampling=True,
            context_missing="LOG_ERROR",
        )
        patch_all()  # auto-instrument boto3, requests, etc.

# Usage as decorator:
# @xray_recorder.capture("intent_agent")
# def intent_agent_node(state):
#     ...


# backend/infrastructure/audit.py
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



# backend/tools/tool_registry.py
from dataclasses import dataclass
from typing import Callable

@dataclass
class ToolDefinition:
    name: str
    function: Callable
    description: str
    allowed_agents: list[str]  # which agents can call this
    requires_approval: bool = False  # needs HITL for this tool
