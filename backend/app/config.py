from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


BACKEND_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """应用配置，从 .env 文件加载。"""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dagents"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/dagents"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    LLM_MODEL: str = ""
    LLM_TEMPERATURE: float = 0.3

    TAVILY_API_KEY: str = ""
    SEARCH_MAX_EXECUTED_QUERIES: int = 10
    SEARCH_MAX_RECOVERY_QUERIES: int = 6

    MEMORY_BACKEND: str = "noop"
    MEMORY_TOP_K: int = 8
    MEMORY_WRITEBACK_ENABLED: bool = True

    RETRIEVER_BACKEND: str = "noop"
    RAG_TOP_K: int = 8
    RAG_RERANK_TOP_N: int = 4

    WORKFLOW_NODE_MAX_ATTEMPTS: int = 3
    WORKFLOW_NODE_TIMEOUT_SEC: int = 300
    WORKFLOW_REPORT_TIMEOUT_SEC: int = 900
    WORKFLOW_RETRY_BACKOFF_BASE_SEC: int = 2

    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "dagents-insightflow"
    LANGSMITH_TRACING_V2: bool = False
    LANGSMITH_ENDPOINT: str = ""

    @property
    def langsmith_enabled(self) -> bool:
        """便捷判断：是否已启用 LangSmith 追踪。"""
        return self.LANGSMITH_TRACING_V2 and bool(self.LANGSMITH_API_KEY)

    model_config = SettingsConfigDict(env_file=BACKEND_ROOT / ".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
