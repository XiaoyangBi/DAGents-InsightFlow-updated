from __future__ import annotations

import asyncio
from typing import Any

from app.memory.backend.base import MemoryBackend


class Mem0Backend(MemoryBackend):
    """Optional adapter for a hosted or local mem0 deployment."""

    backend_name = "mem0"

    def __init__(
        self,
        *,
        api_key: str = "",
        config: dict | None = None,
        client: Any | None = None,
    ):
        self.api_key = api_key
        self.config = config or {}
        self._client = client

    async def write(self, items: list[dict], **kwargs) -> list[str]:
        client = self._get_client()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._write_sync, client, items)

    async def recall(self, query: dict, **kwargs) -> list[dict]:
        client = self._get_client()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._recall_sync, client, query)

    async def update(self, memory_id: str, patch: dict, **kwargs) -> dict:
        client = self._get_client()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._update_sync, client, memory_id, patch)

    async def delete(self, memory_id: str, **kwargs) -> None:
        client = self._get_client()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._delete_sync, client, memory_id)

    async def healthcheck(self) -> dict:
        try:
            self._get_client()
        except RuntimeError as exc:
            return {"backend": self.backend_name, "status": "unavailable", "reason": str(exc)}
        return {"backend": self.backend_name, "status": "ok"}

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from mem0 import MemoryClient  # type: ignore
        except ImportError as exc:
            raise RuntimeError("mem0 is not installed") from exc
        kwargs = dict(self.config)
        if self.api_key:
            kwargs["api_key"] = self.api_key
        self._client = MemoryClient(**kwargs)
        return self._client

    @staticmethod
    def _write_sync(client, items: list[dict]) -> list[str]:
        ids: list[str] = []
        for item in items:
            content = str(item.get("content") or "")
            metadata = dict(item.get("document_metadata") or item.get("metadata") or {})
            user_id = str(item.get("owner_id") or item.get("user_id") or "")
            if hasattr(client, "add"):
                result = client.add(content, user_id=user_id, metadata=metadata)
            elif hasattr(client, "write"):
                result = client.write({"content": content, "user_id": user_id, "metadata": metadata})
            else:
                raise RuntimeError("Configured mem0 client does not support add/write")
            ids.append(Mem0Backend._extract_result_id(result))
        return ids

    @staticmethod
    def _recall_sync(client, query: dict) -> list[dict]:
        text_query = str(query.get("topic") or query.get("query") or "")
        user_id = str(query.get("owner_id") or query.get("user_id") or "")
        limit = int(query.get("top_k") or 8)
        filters = dict(query.get("filters") or {})
        if hasattr(client, "search"):
            result = client.search(text_query, user_id=user_id, limit=limit, filters=filters)
        elif hasattr(client, "recall"):
            result = client.recall({"query": text_query, "user_id": user_id, "limit": limit, "filters": filters})
        else:
            raise RuntimeError("Configured mem0 client does not support search/recall")
        if isinstance(result, dict):
            if isinstance(result.get("results"), list):
                return result["results"]
            if isinstance(result.get("memories"), list):
                return result["memories"]
        return list(result or [])

    @staticmethod
    def _update_sync(client, memory_id: str, patch: dict) -> dict:
        if hasattr(client, "update"):
            result = client.update(memory_id=memory_id, data=patch)
        else:
            raise RuntimeError("Configured mem0 client does not support update")
        return result if isinstance(result, dict) else {"id": memory_id, "result": result}

    @staticmethod
    def _delete_sync(client, memory_id: str) -> None:
        if hasattr(client, "delete"):
            client.delete(memory_id=memory_id)
            return
        raise RuntimeError("Configured mem0 client does not support delete")

    @staticmethod
    def _extract_result_id(result) -> str:
        if isinstance(result, dict):
            return str(result.get("id") or result.get("memory_id") or "")
        return str(result or "")
