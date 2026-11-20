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