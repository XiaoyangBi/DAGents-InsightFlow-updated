from __future__ import annotations

import uuid

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.memory_document import MemoryDocument


async def create_memory_document(db: AsyncSession, **values) -> MemoryDocument:
    document = MemoryDocument(**values)
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def list_memory_documents_for_owner(
    db: AsyncSession,
    owner_id: uuid.UUID,
    *,
    limit: int = 20,
) -> list[MemoryDocument]:
    result = await db.execute(
        select(MemoryDocument)
        .where(MemoryDocument.owner_id == owner_id)
        .order_by(MemoryDocument.updated_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def recall_memory_documents(
    db: AsyncSession,
    *,
    owner_id: uuid.UUID | None = None,
    workflow_id: uuid.UUID | None = None,
    topic: str = "",
    memory_types: list[str] | None = None,
    limit: int = 8,
) -> list[MemoryDocument]:
    stmt = select(MemoryDocument)
    if owner_id is not None:
        stmt = stmt.where(MemoryDocument.owner_id == owner_id)
    if workflow_id is not None:
        stmt = stmt.where(
            or_(MemoryDocument.workflow_id == workflow_id, MemoryDocument.workflow_id.is_(None))
        )
    if memory_types:
        stmt = stmt.where(MemoryDocument.memory_type.in_(memory_types))
    if topic.strip():
        like_term = f"%{topic.strip()}%"
        stmt = stmt.where(
            or_(
                MemoryDocument.title.ilike(like_term),
                MemoryDocument.content.ilike(like_term),
                MemoryDocument.summary.ilike(like_term),
            )
        )
    result = await db.execute(
        stmt.order_by(MemoryDocument.updated_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def get_memory_document(db: AsyncSession, memory_id: uuid.UUID) -> MemoryDocument | None:
    return await db.get(MemoryDocument, memory_id)


async def delete_memory_document(db: AsyncSession, memory_id: uuid.UUID) -> None:
    await db.execute(delete(MemoryDocument).where(MemoryDocument.id == memory_id))
    await db.commit()
