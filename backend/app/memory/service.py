from __future__ import annotations

import uuid

from app.memory.backend.base import MemoryBackend


class MemoryService:
    """Thin application-facing wrapper around the pluggable memory backend."""

    def __init__(self, backend: MemoryBackend):
        self.backend = backend

    async def list_memories(
        self,
        *,
        owner_id: uuid.UUID | str,
        workflow_id: uuid.UUID | str | None = None,
        topic: str = "",
        memory_types: list[str] | None = None,
        top_k: int = 20,
    ) -> list[dict]:
        return await self.backend.recall(
            {
                "owner_id": str(owner_id),
                "workflow_id": str(workflow_id) if workflow_id else "",
                "topic": topic,
                "memory_types": memory_types or [],
                "top_k": top_k,
            }
        )

    async def write_memories(self, items: list[dict]) -> list[str]:
        return await self.backend.write(items)

    async def update_memory(self, memory_id: str, patch: dict) -> dict:
        return await self.backend.update(memory_id, patch)

    async def delete_memory(self, memory_id: str) -> None:
        await self.backend.delete(memory_id)
