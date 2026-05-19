import time
from collections.abc import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram

from app.models.llm_request import LLMRequest

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
HTTP_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)
LLM_REQUESTS = Counter(
    "llm_requests_total",
    "Total LLM requests",
    ["model", "status", "suspicious"],
)
LLM_TOKENS = Counter(
    "llm_tokens_total",
    "Total LLM tokens",
    ["model", "token_type"],
)
LLM_COST = Counter(
    "llm_estimated_cost_usd_total",
    "Estimated LLM cost in USD",
    ["model"],
)
LLM_LATENCY = Histogram(
    "llm_request_duration_seconds",
    "LLM provider request latency in seconds",
    ["model", "status"],
)


async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    latency = time.perf_counter() - start
    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)
    HTTP_REQUESTS.labels(request.method, path, str(response.status_code)).inc()
    HTTP_LATENCY.labels(request.method, path).observe(latency)
    return response


def record_llm_request(record: LLMRequest) -> None:
    status = "error" if record.is_error else "success"
    suspicious = "true" if record.is_suspicious else "false"
    LLM_REQUESTS.labels(record.model, status, suspicious).inc()
    LLM_TOKENS.labels(record.model, "prompt").inc(record.prompt_tokens)
    LLM_TOKENS.labels(record.model, "completion").inc(record.completion_tokens)
    LLM_COST.labels(record.model).inc(record.estimated_cost_usd)
    LLM_LATENCY.labels(record.model, status).observe(record.latency_ms / 1000)
