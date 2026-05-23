from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.services.workflow_service import (
    create_workflow,
    get_workflow_by_id,
    get_user_workflows,
)


router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_new_workflow(
    title: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    workflow = await create_workflow(db, current_user.id, title)
    return {"workflow_id": str(workflow.id), "title": workflow.title, "status": workflow.status}


@router.get("")
async def list_my_workflows(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    workflows = await get_user_workflows(db, current_user.id)
    return [{"id": str(w.id), "title": w.title, "status": w.status, "created_at": w.created_at} for w in workflows]


@router.get("/{workflow_id}")
async def get_workflow_detail(
    workflow_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    workflow = await get_workflow_by_id(db, workflow_id, current_user.id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return {
        "id": str(workflow.id),
        "title": workflow.title,
        "status": workflow.status,
        "config": workflow.config,
        "created_at": workflow.created_at
    }
