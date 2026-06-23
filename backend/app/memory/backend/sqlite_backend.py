from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models.memory_document import MemoryDocument
from app.db.queries.memory_queries import (
    create_memory_document,
    delete_memory_document,
    get_memory_document,
    recall_memory_documents,
)

from app.memory.backend.base import MemoryBackend


class SQLiteMemoryBackend(MemoryBackend):
    """Local fallback backend backed by the app database."""

    backend_name = "sqlite"

    def __init__(
        self,
        *,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
        db_session: AsyncSession | None = None,
    ):
        self.session_factory = session_factory
        self.db_session = db_session

    @asynccontextmanager
    async def _session_scope(self) -> AsyncIterator[AsyncSession]:
        if self.db_session is not None:
            yield self.db_session
            return
        if self.session_factory is None:
            raise RuntimeError("SQLiteMemoryBackend requires a db_session or session_factory")
        async with self.session_factory() as session:
            yield session

    async def write(self, items: list[dict], **kwargs) -> list[str]:
        ids: list[str] = []
        async with self._session_scope() as session:
            for item in items:
                owner_id = self._coerce_uuid(item.get("owner_id"))
                if owner_id is None:
                    raise ValueError("owner_id is required to persist memory")
                workflow_id = self._coerce_uuid(item.get("workflow_id"))
                document = await create_memory_document(
                    session,
                    owner_id=owner_id,
                    workflow_id=workflow_id,
                    memory_type=str(item.get("memory_type") or "note"),
                    scope=str(item.get("scope") or "user"),
                    title=str(item.get("title") or item.get("summary") or "Untitled Memory"),
                    content=str(item.get("content") or ""),
                    summary=str(item.get("summary") or "") or None,
                    source=str(item.get("source") or "workflow"),
                    document_metadata=dict(item.get("document_metadata") or item.get("metadata") or {}),
                )
                ids.append(str(document.id))
        return ids

    async def recall(self, query: dict, **kwargs) -> list[dict]:
        async with self._session_scope() as session:
            documents = await recall_memory_documents(
                session,
                owner_id=self._coerce_uuid(query.get("owner_id")),
                workflow_id=self._coerce_uuid(query.get("workflow_id")),
                topic=str(query.get("topic") or ""),
                memory_types=list(query.get("memory_types") or []),
                limit=int(query.get("top_k") or 8),
            )
        return [self._serialize(document) for document in documents]

    async def update(self, memory_id: str, patch: dict, **kwargs) -> dict:
        async with self._session_scope() as session:
            document = await get_memory_document(session, uuid.UUID(memory_id))
            if document is None:
                raise KeyError(f"Memory {memory_id} not found")
            if "memory_type" in patch:
                document.memory_type = str(patch["memory_type"])
            if "scope" in patch:
                document.scope = str(patch["scope"])
            if "title" in patch:
                document.title = str(patch["title"])
            if "content" in patch:
                document.content = str(patch["content"])
            if "summary" in patch:
                document.summary = str(patch["summary"]) if patch["summary"] is not None else None
            if "source" in patch:
                document.source = str(patch["source"])
            if "document_metadata" in patch or "metadata" in patch:
                document.document_metadata = dict(
                    patch.get("document_metadata") or patch.get("metadata") or {}
                )
            await session.commit()
            await session.refresh(document)
            return self._serialize(document)

    async def delete(self, memory_id: str, **kwargs) -> None:
        async with self._session_scope() as session:
            await delete_memory_document(session, uuid.UUID(memory_id))

    async def healthcheck(self) -> dict:
        return {"backend": self.backend_name, "status": "ok"}

    @staticmethod
    def _coerce_uuid(value) -> uuid.UUID | None:
        if not value:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))

    @staticmethod
    def _serialize(document: MemoryDocument) -> dict:
        return {
            "id": str(document.id),
            "owner_id": str(document.owner_id),
            "workflow_id": str(document.workflow_id) if document.workflow_id else "",
            "memory_type": document.memory_type,
            "scope": document.scope,
            "title": document.title,
            "content": document.content,
            "summary": document.summary or "",
            "source": document.source,
            "document_metadata": dict(document.document_metadata or {}),
            "updated_at": document.updated_at.isoformat() if document.updated_at else "",
        }
