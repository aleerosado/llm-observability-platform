from sqlalchemy import Integer, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.llm_request import LLMRequest
from app.schemas.metrics import DashboardMetrics


class LLMRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, request: LLMRequest) -> LLMRequest:
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def list_recent(self, limit: int = 50) -> list[LLMRequest]:
        stmt = select(LLMRequest).order_by(desc(LLMRequest.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def dashboard_metrics(self) -> DashboardMetrics:
        stmt = select(
            func.count(LLMRequest.id),
            func.coalesce(func.sum(LLMRequest.estimated_cost_usd), 0.0),
            func.coalesce(func.avg(LLMRequest.latency_ms), 0.0),
            func.coalesce(func.sum(LLMRequest.is_error.cast(Integer)), 0),
            func.coalesce(func.sum(LLMRequest.is_suspicious.cast(Integer)), 0),
            func.coalesce(func.sum(LLMRequest.total_tokens), 0),
        )
        row = (await self.session.execute(stmt)).one()
        return DashboardMetrics(
            total_requests=row[0],
            total_cost_usd=round(float(row[1]), 6),
            average_latency_ms=round(float(row[2]), 2),
            error_count=int(row[3]),
            suspicious_count=int(row[4]),
            total_tokens=int(row[5]),
        )
