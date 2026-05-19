import time
from dataclasses import dataclass

from openai import AsyncOpenAI

from app.core.config import Settings


@dataclass(frozen=True)
class LLMProviderResult:
    response_text: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class OpenAIService:
    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for /chat requests.")
        self.client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout_seconds)

    async def complete(self, prompt: str, model: str) -> LLMProviderResult:
        start = time.perf_counter()
        response = await self.client.responses.create(
            model=model,
            input=prompt,
        )
        latency_ms = (time.perf_counter() - start) * 1000
        usage = response.usage
        prompt_tokens = getattr(usage, "input_tokens", 0) if usage else 0
        completion_tokens = getattr(usage, "output_tokens", 0) if usage else 0
        total_tokens = getattr(usage, "total_tokens", prompt_tokens + completion_tokens) if usage else 0
        return LLMProviderResult(
            response_text=response.output_text,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )
