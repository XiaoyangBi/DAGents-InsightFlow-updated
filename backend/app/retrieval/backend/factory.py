from __future__ import annotations

from app.config import Settings, get_settings
from app.retrieval.backend.base import NullRetrieverBackend, RetrieverBackend


def build_retriever_backend(*, settings: Settings | None = None) -> RetrieverBackend:
    resolved = settings or get_settings()
    backend_name = (resolved.RETRIEVER_BACKEND or "noop").strip().lower()
    return NullRetrieverBackend(backend_name or "noop")
