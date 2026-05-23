from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class EventType(str, Enum):
    NODE_START = "node_start"
    NODE_COMPLETE = "node_complete"
    NODE_ERROR = "node_error"
    REVIEW_PASS = "review_pass"
    REVIEW_FAIL = "review_fail"
    REVIEW_REROUTE = "review_reroute"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_COMPLETE = "workflow_complete"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_PAUSED = "workflow_paused"
    CONTEXT_COMPRESSED = "context_compressed"


class EventPayload(BaseModel):
    pass
