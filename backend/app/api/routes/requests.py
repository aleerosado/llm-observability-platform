from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.llm_request_repository import LLMRequestRepository
from app.schemas.chat import ChatResponse
from app.schemas.metrics import DashboardMetrics

router = APIRouter(tags=["requests"])
DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def _to_response(record) -> ChatResponse:
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


@router.get("/requests", response_model=list[ChatResponse])
async def recent_requests(
    session: DbSession,
    limit: int = Query(default=25, ge=1, le=100),
) -> list[ChatResponse]:
    records = await LLMRequestRepository(session).list_recent(limit=limit)
    return [_to_response(record) for record in records]


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def dashboard_metrics(session: DbSession) -> DashboardMetrics:
    return await LLMRequestRepository(session).dashboard_metrics()
