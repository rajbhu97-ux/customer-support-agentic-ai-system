from fastapi import APIRouter, HTTPException, Depends
from backend.hitl.approval import ApprovalManager
from config.settings import settings
from pydantic import BaseModel

router = APIRouter()


def get_approval_manager():
    return ApprovalManager(
        table_name=settings.DYNAMO_TABLE_NAME,
        sns_topic_arn=settings.SNS_TOPIC_NAME,
        region=settings.AWS_REGION,
    )


class ResolveRequest(BaseModel):
    resolved_by: str


@router.get("/{request_id}")
async def get_approval(
    request_id: str, mgr: ApprovalManager = Depends(get_approval_manager)
):
    item = mgr.get_status(request_id=request_id)
    if not item:
        raise HTTPException(404, "Approval request not found")
    return item


@router.post("/{request_id}/approve")
async def approve(
    request_id: str,
    body: ResolveRequest,
    mgr: ApprovalManager = Depends(get_approval_manager),
):
    if not mgr.approve(request_id=request_id, resolved_by=body.resolved_by):
        raise HTTPException(404, "Already resolved or expired")
    return {"status": "APPROVED"}


@router.post("/{request_id}/reject")
async def reject(
    request_id: str,
    body: ResolveRequest,
    mgr: ApprovalManager = Depends(get_approval_manager),
):
    if not mgr.reject(request_id=request_id, resolved_by=body.resolved_by):
        raise HTTPException(404, "Already resolved or expired")
    return {"status": "REJECTED"}


@router.get("/session/{session_id}/pending")
async def pending_for_session(
    session_id: str, mgr: ApprovalManager = Depends(get_approval_manager)
):
    return mgr.get_pending_for_session(session_id)
