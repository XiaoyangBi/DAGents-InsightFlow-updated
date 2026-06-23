from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db.session import async_session_factory
from app.memory.backend.base import MemoryBackend, NullMemoryBackend
from app.memory.backend.mem0_backend import Mem0Backend
from app.memory.backend.sqlite_backend import SQLiteMemoryBackend


def build_memory_backend(
    *,
    settings: Settings | None = None,
    db_session: AsyncSession | None = None,
) -> MemoryBackend:
    resolved = settings or get_settings()
    backend_name = (resolved.MEMORY_BACKEND or "noop").strip().lower()
    if backend_name in {"", "noop", "none", "disabled"}:
        return NullMemoryBackend(backend_name or "noop")
    if backend_name in {"sqlite", "local", "sqlalchemy"}:
        return SQLiteMemoryBackend(
            db_session=db_session,
            session_factory=None if db_session is not None else async_session_factory,
        )
    if backend_name == "mem0":
        return Mem0Backend(api_key=resolved.MEM0_API_KEY)
    return NullMemoryBackend(backend_name)
