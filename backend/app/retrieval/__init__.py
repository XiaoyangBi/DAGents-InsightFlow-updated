"""Pluggable retrieval backends for V2."""

from app.retrieval.backend.factory import build_retriever_backend

__all__ = ["build_retriever_backend"]
