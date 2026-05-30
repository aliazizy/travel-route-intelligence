from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Travel Route Intelligence"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:4000"]
    log_level: str = "INFO"
    mock_provider_latency_ms: int = 0
    llm_provider: Literal["mock", "openai", "azure_openai"] = "mock"
    openai_api_key: str | None = None
    openai_model: str = "model-router"
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = "2025-01-01-preview"
    geocoder_provider: Literal["mock", "google", "mapbox"] = "mock"
    google_maps_api_key: str | None = None
    routing_provider: Literal["mock", "openrouteservice", "osrm"] = "mock"
    openrouteservice_api_key: str | None = None
    geocoding_cache_ttl_seconds: int = 86_400
    routing_cache_ttl_seconds: int = 86_400

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
