from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api.routes import chat, health, requests
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import init_db
from app.observability.logging_middleware import RequestLoggingMiddleware
from app.observability.metrics import metrics_middleware
from app.observability.tracing import configure_tracing


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    configure_tracing(app, settings)
    if settings.auto_create_tables:
        await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Production-style MVP for monitoring LLM latency, cost, tokens, errors, prompts, "
            "responses, and security signals."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.middleware("http")(metrics_middleware)

    app.include_router(health.router)
    app.include_router(chat.router, prefix="/api")
    app.include_router(requests.router, prefix="/api")
    app.mount("/metrics", make_asgi_app())
    return app


app = create_app()
