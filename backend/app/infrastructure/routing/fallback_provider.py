import structlog

from app.domain.models.route import RouteCalculationRequest, RouteCalculationResponse
from app.infrastructure.routing.base import RoutingProvider, RoutingProviderError

logger = structlog.get_logger(__name__)


class FallbackRoutingProvider:
    def __init__(self, primary: RoutingProvider, fallback: RoutingProvider) -> None:
        self.primary = primary
        self.fallback = fallback

    async def calculate(self, request: RouteCalculationRequest) -> RouteCalculationResponse:
        try:
            return await self.primary.calculate(request)
        except RoutingProviderError:
            logger.warning("routing_primary_failed_using_fallback")
            response = await self.fallback.calculate(request)
            return RouteCalculationResponse(
                route_segments=response.route_segments,
                total_distance_meters=response.total_distance_meters,
                total_duration_seconds=response.total_duration_seconds,
                warnings=[
                    "Primary routing provider failed; used fallback mock routing for this request.",
                    *response.warnings,
                ],
            )
