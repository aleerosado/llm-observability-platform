from functools import lru_cache
from typing import Annotated

from pydantic import AnyHttpUrl, Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LLM Observability Platform"
    app_version: str = "0.1.0"
    environment: str = "local"
    log_level: str = "INFO"
    api_prefix: str = "/api"

    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/llm_observability"
    )
    auto_create_tables: bool = True

    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"
    openai_timeout_seconds: float = 30.0

    cors_origins: list[Annotated[str, AnyHttpUrl] | str] = ["http://localhost:3000"]

    otel_service_name: str = "llm-observability-backend"
    otel_exporter_otlp_endpoint: str | None = None
    tracing_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
