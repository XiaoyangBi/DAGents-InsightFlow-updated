import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.workflow import Workflow


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


async def get_workflow_by_id(db: AsyncSession, workflow_id: str, owner_id: uuid.UUID) -> Workflow | None:
    result = await db.execute(
        select(Workflow).where(Workflow.id == uuid.UUID(workflow_id), Workflow.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def get_user_workflows(db: AsyncSession, owner_id: uuid.UUID, limit: int = 20) -> List[Workflow]:
    result = await db.execute(
        select(Workflow).where(Workflow.owner_id == owner_id).order_by(Workflow.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())
