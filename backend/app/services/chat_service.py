import time

from opentelemetry import trace
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.core.config import get_settings
from app.models.llm_request import LLMRequest
from app.observability.metrics import record_llm_request
from app.repositories.llm_request_repository import LLMRequestRepository
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.cost import CostEstimator
from app.services.openai_service import OpenAIService
from app.services.security import PromptSecurityService

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)


class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.settings = get_settings()
        self.repository = LLMRequestRepository(session)
        self.security = PromptSecurityService()
        self.cost_estimator = CostEstimator()

    async def chat(self, payload: ChatRequest) -> ChatResponse:
        model = payload.model or self.settings.openai_model
        flags = self.security.analyze(payload.prompt)
        trace_id = self._current_trace_id()

        with tracer.start_as_current_span("llm.chat") as span:
            span.set_attribute("llm.model", model)
            span.set_attribute("llm.prompt.suspicious", bool(flags))
            start = time.perf_counter()
            try:
                result = await OpenAIService(self.settings).complete(payload.prompt, model)
                estimated_cost = self.cost_estimator.estimate(
                    model=model,
                    input_tokens=result.prompt_tokens,
                    output_tokens=result.completion_tokens,
                )
                record = LLMRequest(
                    trace_id=trace_id,
                    model=model,
                    prompt=payload.prompt,
                    response=result.response_text,
                    latency_ms=round(result.latency_ms, 2),
                    prompt_tokens=result.prompt_tokens,
                    completion_tokens=result.completion_tokens,
                    total_tokens=result.total_tokens,
                    estimated_cost_usd=estimated_cost,
                    is_error=False,
                    is_suspicious=bool(flags),
                    security_flags=",".join(flags),
                )
            except Exception as exc:
                latency_ms = (time.perf_counter() - start) * 1000
                logger.exception("llm_request_failed", model=model)
                record = LLMRequest(
                    trace_id=trace_id,
                    model=model,
                    prompt=payload.prompt,
                    response=None,
                    latency_ms=round(latency_ms, 2),
                    is_error=True,
                    error_message=str(exc),
                    is_suspicious=bool(flags),
                    security_flags=",".join(flags),
                )

            saved = await self.repository.create(record)
            record_llm_request(saved)
            span.set_attribute("llm.request_id", saved.id)
            span.set_attribute("llm.tokens.total", saved.total_tokens)
            span.set_attribute("llm.cost.estimated_usd", saved.estimated_cost_usd)
            return self._to_response(saved)

    def _to_response(self, record: LLMRequest) -> ChatResponse:
        return ChatResponse(
            request_id=record.id,
            trace_id=record.trace_id,
            model=record.model,
            response=record.response,
            latency_ms=record.latency_ms,
            prompt_tokens=record.prompt_tokens,
            completion_tokens=record.completion_tokens,
            total_tokens=record.total_tokens,
            estimated_cost_usd=record.estimated_cost_usd,
            is_error=record.is_error,
            error_message=record.error_message,
            is_suspicious=record.is_suspicious,
            security_flags=[flag for flag in record.security_flags.split(",") if flag],
            created_at=record.created_at,
        )

    def _current_trace_id(self) -> str | None:
        span_context = trace.get_current_span().get_span_context()
        if not span_context.is_valid:
            return None
        return format(span_context.trace_id, "032x")
