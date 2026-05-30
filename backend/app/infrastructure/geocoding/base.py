from abc import ABC, abstractmethod

from app.domain.models.place import PlaceResolutionRequest, PlaceResolutionResponse


class GeocoderProviderError(Exception):
    """Raised when a geocoding provider cannot complete a resolution request."""


class GeocoderProvider(ABC):
    @abstractmethod
    async def resolve(self, request: PlaceResolutionRequest) -> PlaceResolutionResponse:
        """Resolve candidate place names into coordinates and alternatives."""
