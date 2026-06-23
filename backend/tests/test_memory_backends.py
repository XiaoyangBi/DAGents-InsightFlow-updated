import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.db.base import Base
from app.memory.backend.factory import build_memory_backend
from app.memory.backend.mem0_backend import Mem0Backend
from app.memory.backend.sqlite_backend import SQLiteMemoryBackend


@pytest.mark.asyncio
async def test_sqlite_memory_backend_round_trip():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    backend = SQLiteMemoryBackend(session_factory=session_factory)
    owner_id = uuid.uuid4()

    created_ids = await backend.write([
        {
            "owner_id": owner_id,
            "memory_type": "user_preference",
            "title": "偏好结论先行",
            "content": "用户偏好结论先行、带引用。",
            "document_metadata": {"source": "test"},
        }
    ])
    recalled = await backend.recall({"owner_id": owner_id, "topic": "结论先行", "top_k": 5})

    assert len(created_ids) == 1
    assert recalled[0]["memory_type"] == "user_preference"
    assert recalled[0]["document_metadata"]["source"] == "test"


def test_memory_backend_factory_supports_sqlite_and_mem0():
    sqlite_backend = build_memory_backend(
        settings=Settings(JWT_SECRET_KEY="test", MEMORY_BACKEND="sqlite")
    )
    mem0_backend = build_memory_backend(
        settings=Settings(JWT_SECRET_KEY="test", MEMORY_BACKEND="mem0", MEM0_API_KEY="demo")
    )

    assert isinstance(sqlite_backend, SQLiteMemoryBackend)
    assert isinstance(mem0_backend, Mem0Backend)
