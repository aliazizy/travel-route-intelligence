from app.core.config import Settings
from app.core.errors import AppError, ErrorCode
from app.infrastructure.cache.in_memory import InMemoryTTLCache
from app.infrastructure.routing.base import RoutingProvider
from app.infrastructure.routing.fallback_provider import FallbackRoutingProvider
from app.infrastructure.routing.mock_provider import MockRoutingProvider
from app.infrastructure.routing.openrouteservice_provider import OpenRouteServiceRoutingProvider


_routing_cache = InMemoryTTLCache()


def build_routing_provider(settings: Settings) -> RoutingProvider:
    if settings.routing_provider == "mock":
        return MockRoutingProvider()

    if settings.routing_provider == "openrouteservice":
        if not settings.openrouteservice_api_key:
            raise AppError(
                ErrorCode.routing_failed,
                "OpenRouteService routing is selected but OPENROUTESERVICE_API_KEY is missing.",
                details={"missing": ["OPENROUTESERVICE_API_KEY"]},
                status_code=500,
            )
        return FallbackRoutingProvider(
            primary=OpenRouteServiceRoutingProvider(
                api_key=settings.openrouteservice_api_key,
                cache=_routing_cache,
                cache_ttl_seconds=settings.routing_cache_ttl_seconds,
            ),
            fallback=MockRoutingProvider(),
        )

    raise AppError(
        ErrorCode.routing_failed,
        f"Routing provider '{settings.routing_provider}' is not implemented yet.",
        recoverable=True,
        status_code=501,
    )
