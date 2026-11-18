import uuid

from fastapi import APIRouter, Depends
from backend.api.models.model import ChatRequest, ChatResponse
from backend.middleware.auth import get_current_user
from backend.middleware.authorization import require_customer, require_agent, require_admin


router = APIRouter()


@router.post(
    "/chat", response_model=ChatResponse, dependencies=[Depends(require_customer)]
)
async def chat(request: ChatRequest, user: Depends(get_current_user)):
    require_customer(user)
    initial_state = {
        "raw_user_message": request.get("message"),
        "user_id": user.get("user_id"),
        "session_id": user.get("session_id") or str(uuid.uuid4()),
        "user_role": user.get("role"),
        "conversation_history": [],
    }
    result = app_graph.invoke(initial_state)
    return ChatResponse(rsponse=result.get("final_response", ""))


@router.get("/tickets")
async def list_tickets(user: dict = Depends(get_current_user)):
    require_agent(user)


@router.post("/admin/reload-kb")
async def reload_knowledge_base(user: dict = Depends(get_current_user)):
    require_admin(user)