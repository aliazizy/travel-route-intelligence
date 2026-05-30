from abc import ABC, abstractmethod

from app.domain.models.route import RouteCalculationRequest, RouteCalculationResponse


class RoutingProviderError(Exception):
    """Raised when a routing provider cannot calculate requested routes."""


class RoutingProvider(ABC):
    @abstractmethod
    async def calculate(self, request: RouteCalculationRequest) -> RouteCalculationResponse:
        """Calculate route geometry and travel estimates for ordered itinerary steps."""
