from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12_000)
    model: str | None = Field(default=None, max_length=128)


class ChatResponse(BaseModel):
    request_id: str
    trace_id: str | None
    model: str
    response: str | None
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    is_error: bool
    error_message: str | None
    is_suspicious: bool
    security_flags: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}
