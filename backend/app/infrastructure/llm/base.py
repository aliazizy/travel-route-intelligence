from abc import ABC, abstractmethod

from app.domain.models.itinerary import ParseItineraryResponse, TravelRequest


class LLMProviderError(Exception):
    """Raised when an LLM provider cannot produce a valid extraction response."""


class LLMProvider(ABC):
    @abstractmethod
    async def parse_itinerary(self, request: TravelRequest) -> ParseItineraryResponse:
        """Extract structured itinerary facts without resolving coordinates."""
