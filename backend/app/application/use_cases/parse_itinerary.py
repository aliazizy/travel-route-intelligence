from app.core.errors import AppError, ErrorCode
from app.domain.models.itinerary import ParsedPlaceRef, ParseItineraryResponse, TravelRequest
from app.infrastructure.llm.base import LLMProvider
from app.infrastructure.llm.base import LLMProviderError


class ParseItineraryUseCase:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    async def execute(self, request: TravelRequest) -> ParseItineraryResponse:
        try:
            response = await self.provider.parse_itinerary(request)
        except LLMProviderError as exc:
            raise AppError(
                ErrorCode.llm_extraction_failed,
                str(exc),
                recoverable=True,
                status_code=502,
            ) from exc

        self._apply_deterministic_airport_rules(request, response)
        return response

    def _apply_deterministic_airport_rules(
        self,
        request: TravelRequest,
        response: ParseItineraryResponse,
    ) -> None:
        text = request.request_text.lower()
        if (
            response.parsed_itinerary.departure is None
            and "heathrow" in text
            and any(token in text for token in ["return", "depart", "departure", "fly back"])
        ):
            response.parsed_itinerary.departure = ParsedPlaceRef(
                name="Heathrow",
                place_type="airport",
                country_hint=request.default_country or "United Kingdom",
                role="departure",
                locked=True,
                confidence=0.88,
                inferred=False,
            )
            response.warnings = [
                warning
                for warning in response.warnings
                if warning != "Departure airport was not explicitly identified."
            ]
