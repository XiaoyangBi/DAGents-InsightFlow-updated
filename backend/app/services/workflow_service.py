import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.workflow import Workflow
from app.db.queries.workflow_queries import get_workflow_by_id


async def create_workflow(db: AsyncSession, owner_id: uuid.UUID, title: str) -> Workflow:
    workflow = Workflow(
        id=uuid.uuid4(),
        owner_id=owner_id,
        title=title,
        status="configuring"
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow


async def confirm_interview(db: AsyncSession, workflow_id: str, owner_id: uuid.UUID) -> Workflow | None:
    """确认访谈配置已完成。校验 status=configuring 且 config 已提取，返回工作流供前端展示确认信息。"""
    workflow = await get_workflow_by_id(db, workflow_id, owner_id)
    if not workflow or workflow.status != "configuring":
        return None
    if not workflow.config or not workflow.config.get("target_product"):
        return None
    return workflow


async def start_workflow(db: AsyncSession, workflow_id: str, owner_id: uuid.UUID) -> Workflow | None:
    """将工作流状态转为 running，准备启动后台任务。"""
    workflow = await get_workflow_by_id(db, workflow_id, owner_id)
    if not workflow or workflow.status != "configuring":
        return None
    if not workflow.config or not workflow.config.get("target_product"):
        return None
    workflow.status = "running"
    workflow.current_phase = "collecting"
    await db.commit()
    await db.refresh(workflow)
    return workflow


async def cancel_workflow(db: AsyncSession, workflow_id: str, owner_id: uuid.UUID) -> Workflow | None:
    """取消工作流。已完成或已取消的工作流无法取消。"""
    workflow = await get_workflow_by_id(db, workflow_id, owner_id)
    if not workflow or workflow.status in ("completed", "cancelled"):
        return None
    workflow.status = "cancelled"
    await db.commit()
    await db.refresh(workflow)
    return workflow


async def delete_workflow(db: AsyncSession, workflow_id: str, owner_id: uuid.UUID) -> bool:
    """物理删除工作流（级联删除所有关联数据）。"""
    workflow = await get_workflow_by_id(db, workflow_id, owner_id)
    if not workflow:
        return False
    await db.delete(workflow)
    await db.commit()
    return True
