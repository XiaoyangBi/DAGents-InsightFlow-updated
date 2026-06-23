import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent
from app.context.assembler import ContextAssembler
from app.core.runtime.context import AgentContext
from app.memory.backend.base import MemoryBackend
from app.retrieval.backend.base import RetrieverBackend


class _EchoSchema(BaseModel):
    ok: bool


class _DummyAgent(BaseAgent):
    node_name = "dummy"


class _MemorySpy(MemoryBackend):
    backend_name = "memory-spy"

    def __init__(self):
        self.recall_calls: list[dict] = []

    async def write(self, items: list[dict], **kwargs) -> list[str]:
        return ["memory-1"]

    async def recall(self, query: dict, **kwargs) -> list[dict]:
        self.recall_calls.append(query)
        return [{"memory_type": "user_preference", "content": "偏好结论先行"}]

    async def update(self, memory_id: str, patch: dict, **kwargs) -> dict:
        return {"id": memory_id, **patch}

    async def delete(self, memory_id: str, **kwargs) -> None:
        return None

    async def healthcheck(self) -> dict:
        return {"backend": self.backend_name, "status": "ok"}


class _RetrieverSpy(RetrieverBackend):
    backend_name = "retriever-spy"

    def __init__(self):
        self.retrieve_calls: list[dict] = []

    async def index(self, documents: list[dict], **kwargs) -> list[str]:
        return ["doc-1"]

    async def retrieve(self, query: dict, **kwargs) -> list[dict]:
        self.retrieve_calls.append(query)
        return [{"title": "历史报告", "snippet": "pricing insight"}]

    async def delete(self, document_id: str, **kwargs) -> None:
        return None

    async def healthcheck(self) -> dict:
        return {"backend": self.backend_name, "status": "ok"}


def _mock_ctx() -> AgentContext:
    return AgentContext(
        workflow_id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        node_id="analysis",
        iteration=1,
        events=SimpleNamespace(
            emit=AsyncMock(),
            progress=AsyncMock(),
            stream_token=AsyncMock(),
        ),
        memory_context={"active_thread": {"focus_dimensions": ["定价"]}},
        rag_context={"chunks": [{"title": "历史报告"}]},
        context_trace={"node_id": "analysis"},
    )


@pytest.mark.asyncio
async def test_context_assembler_builds_memory_and_rag_context():
    assembler = ContextAssembler(memory_backend=_MemorySpy(), retriever_backend=_RetrieverSpy())

    bundle = await assembler.build_context(
        workflow_id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        node_id="analysis",
        iteration=2,
        state={
            "config": {
                "target_product": "Notion",
                "product_category": "AI 产品 / 智能助手",
                "focus_dimensions": ["定价", "定位"],
                "extra_requirements": "关注 onboarding",
            }
        },
    )

    assert bundle.memory_context["product_profile"]["target_product"] == "Notion"
    assert bundle.memory_context["recalled_memories"][0]["memory_type"] == "user_preference"
    assert bundle.rag_context["chunks"][0]["title"] == "历史报告"
    assert bundle.context_trace["memory_hits"] == 1
    assert bundle.context_trace["rag_hits"] == 1


@pytest.mark.asyncio
async def test_context_assembler_respects_workflow_feature_flags():
    memory_backend = _MemorySpy()
    retriever_backend = _RetrieverSpy()
    assembler = ContextAssembler(memory_backend=memory_backend, retriever_backend=retriever_backend)

    bundle = await assembler.build_context(
        workflow_id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        node_id="report_writing",
        iteration=0,
        state={
            "config": {
                "target_product": "Linear",
                "memory_enabled": False,
                "rag_enabled": False,
            }
        },
    )

    assert memory_backend.recall_calls == []
    assert retriever_backend.retrieve_calls == []
    assert bundle.memory_context["recalled_memories"] == []
    assert bundle.rag_context["chunks"] == []


@pytest.mark.asyncio
async def test_base_agent_injects_context_into_llm_payloads():
    agent = _DummyAgent()
    ctx = _mock_ctx()

    async def _fake_json_model(system_prompt, user_payload, schema, stream_callback=None):
        assert user_payload["memory_context"]["active_thread"]["focus_dimensions"] == ["定价"]
        assert user_payload["rag_context"]["chunks"][0]["title"] == "历史报告"
        assert user_payload["context_trace"]["node_id"] == "analysis"
        return schema(ok=True)

    with patch("app.agents.base_agent.invoke_json_model", side_effect=_fake_json_model):
        result = await agent.invoke_llm(
            "system",
            {"target_product": "Notion"},
            _EchoSchema,
            ctx,
            "dummy-task",
        )

    assert result.ok is True
