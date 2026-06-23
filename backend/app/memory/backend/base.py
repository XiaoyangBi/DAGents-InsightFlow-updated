from __future__ import annotations

from abc import ABC, abstractmethod


class MemoryBackend(ABC):
    """Stable contract for pluggable memory implementations."""

    backend_name = "memory"

    @abstractmethod
    async def write(self, items: list[dict], **kwargs) -> list[str]:
        """Persist memory entries and return their identifiers."""

    @abstractmethod
    async def recall(self, query: dict, **kwargs) -> list[dict]:
        """Recall relevant memory entries for the given structured query."""

    @abstractmethod
    async def update(self, memory_id: str, patch: dict, **kwargs) -> dict:
        """Update an existing memory entry."""

    @abstractmethod
    async def delete(self, memory_id: str, **kwargs) -> None:
        """Delete or invalidate an existing memory entry."""

    @abstractmethod
    async def healthcheck(self) -> dict:
        """Report backend availability and capabilities."""


class NullMemoryBackend(MemoryBackend):
    """Safe no-op backend used until a real memory provider is configured."""

    def __init__(self, backend_name: str = "noop"):
        self.backend_name = backend_name

    async def write(self, items: list[dict], **kwargs) -> list[str]:
        return []

    async def recall(self, query: dict, **kwargs) -> list[dict]:
        return []

    async def update(self, memory_id: str, patch: dict, **kwargs) -> dict:
        return {"id": memory_id, **patch}

    async def delete(self, memory_id: str, **kwargs) -> None:
        return None

    async def healthcheck(self) -> dict:
        return {"backend": self.backend_name, "status": "noop"}
