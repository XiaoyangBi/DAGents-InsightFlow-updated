from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.workflow import WorkflowConfig


class InterviewMessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class InterviewMessage(BaseModel):
    id: Optional[str] = None
    role: InterviewMessageRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InterviewInput(BaseModel):
    user_message: str
    thinking_enabled: bool = False
    analysis_preferences: dict | None = None


class InterviewOutput(BaseModel):
    response: str
    is_complete: bool
    extracted_config: Optional[WorkflowConfig] = None
    suggested_competitors: list[str] = Field(default_factory=list)
