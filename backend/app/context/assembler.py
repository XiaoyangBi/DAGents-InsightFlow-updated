from __future__ import annotations

from dataclasses import dataclass
import uuid

from app.memory.backend.base import MemoryBackend, NullMemoryBackend
from app.retrieval.backend.base import NullRetrieverBackend, RetrieverBackend


@dataclass(frozen=True)
class ContextBundle:
    memory_context: dict
    rag_context: dict
    context_trace: dict


class ContextAssembler:
    """Build one stable context bundle per node execution."""

    def __init__(
        self,
        memory_backend: MemoryBackend | None = None,
        retriever_backend: RetrieverBackend | None = None,
    ):
        self.memory_backend = memory_backend or NullMemoryBackend()
        self.retriever_backend = retriever_backend or NullRetrieverBackend()

    async def build_context(
        self,
        *,
        workflow_id: uuid.UUID,
        run_id: uuid.UUID,
        node_id: str,
        iteration: int,
        state: dict,
    ) -> ContextBundle:
        config = state.get("config") if isinstance(state.get("config"), dict) else {}
        memory_enabled = config.get("memory_enabled", True)
        rag_enabled = config.get("rag_enabled", True)
        memory_query = self._build_memory_query(
            config=config,
            workflow_id=workflow_id,
            node_id=node_id,
            iteration=iteration,
        )
        retrieval_query = self._build_retrieval_query(
            config=config,
            workflow_id=workflow_id,
            node_id=node_id,
            iteration=iteration,
        )

        recalled = await self.memory_backend.recall(memory_query) if memory_enabled else []
        retrieved = await self.retriever_backend.retrieve(retrieval_query) if rag_enabled else []

        memory_context = {
            **self._base_memory_context(config=config, state=state),
            "recalled_memories": recalled,
        }
        rag_context = {
            **self._base_rag_context(config=config, state=state),
            "chunks": retrieved,
        }
        context_trace = {
            "workflow_id": str(workflow_id),
            "run_id": str(run_id),
            "node_id": node_id,
            "iteration": iteration,
            "memory_backend": self.memory_backend.backend_name,
            "retriever_backend": self.retriever_backend.backend_name,
            "memory_enabled": memory_enabled,
            "rag_enabled": rag_enabled,
            "memory_query": memory_query,
            "retrieval_query": retrieval_query,
            "memory_hits": len(recalled),
            "rag_hits": len(retrieved),
        }
        return ContextBundle(
            memory_context=memory_context,
            rag_context=rag_context,
            context_trace=context_trace,
        )

    @staticmethod
    def _base_memory_context(*, config: dict, state: dict) -> dict:
        existing = state.get("memory_context") if isinstance(state.get("memory_context"), dict) else {}
        return {
            "user_profile": existing.get("user_profile") or {},
            "product_profile": existing.get("product_profile") or {
                "active_product_id": config.get("active_product_id", ""),
                "target_product": config.get("target_product", ""),
                "product_category": config.get("product_category", ""),
            },
            "active_thread": existing.get("active_thread") or {
                "research_thread_id": config.get("research_thread_id", ""),
                "focus_dimensions": list(config.get("focus_dimensions") or []),
                "extra_requirements": config.get("extra_requirements", ""),
            },
            "analysis_preferences": existing.get("analysis_preferences") or {},
        }

    @staticmethod
    def _base_rag_context(*, config: dict, state: dict) -> dict:
        existing = state.get("rag_context") if isinstance(state.get("rag_context"), dict) else {}
        return {
            "query": existing.get("query") or config.get("target_product", ""),
            "citations": existing.get("citations") or [],
            "trace": existing.get("trace") or {},
        }

    @staticmethod
    def _build_memory_query(
        *,
        config: dict,
        workflow_id: uuid.UUID,
        node_id: str,
        iteration: int,
    ) -> dict:
        return {
            "owner_id": config.get("owner_id", ""),
            "workflow_id": str(workflow_id),
            "topic": config.get("target_product", ""),
            "node_id": node_id,
            "active_product_id": config.get("active_product_id", ""),
            "research_thread_id": config.get("research_thread_id", ""),
            "focus_dimensions": list(config.get("focus_dimensions") or []),
            "iteration": iteration,
        }

    @staticmethod
    def _build_retrieval_query(
        *,
        config: dict,
        workflow_id: uuid.UUID,
        node_id: str,
        iteration: int,
    ) -> dict:
        return {
            "query": config.get("target_product", ""),
            "workflow_id": str(workflow_id),
            "node_id": node_id,
            "focus_dimensions": list(config.get("focus_dimensions") or []),
            "iteration": iteration,
        }
