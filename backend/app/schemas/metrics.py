from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_requests: int
    total_cost_usd: float
    average_latency_ms: float
    error_count: int
    suspicious_count: int
    total_tokens: int
