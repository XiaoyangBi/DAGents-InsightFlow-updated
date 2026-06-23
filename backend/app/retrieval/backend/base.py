from __future__ import annotations

from abc import ABC, abstractmethod


class RetrieverBackend(ABC):
    """Stable contract for pluggable retrieval implementations."""

    backend_name = "retriever"

    @abstractmethod
    async def index(self, documents: list[dict], **kwargs) -> list[str]:
        """Index new documents and return their identifiers."""

    @abstractmethod
    async def retrieve(self, query: dict, **kwargs) -> list[dict]:
        """Retrieve evidence chunks for a structured query."""

    @abstractmethod
    async def delete(self, document_id: str, **kwargs) -> None:
        """Delete indexed content."""

    @abstractmethod
    async def healthcheck(self) -> dict:
        """Report backend availability and capabilities."""


class NullRetrieverBackend(RetrieverBackend):
    """Safe no-op backend used until a real retriever is configured."""

    def __init__(self, backend_name: str = "noop"):
        self.backend_name = backend_name

    async def index(self, documents: list[dict], **kwargs) -> list[str]:
        return []

    async def retrieve(self, query: dict, **kwargs) -> list[dict]:
        return []

    async def delete(self, document_id: str, **kwargs) -> None:
        return None

    async def healthcheck(self) -> dict:
        return {"backend": self.backend_name, "status": "noop"}
