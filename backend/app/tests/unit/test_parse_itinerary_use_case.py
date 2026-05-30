import pytest

from app.application.use_cases.parse_itinerary import ParseItineraryUseCase
from app.domain.models.itinerary import ParsedItinerary, ParseItineraryResponse, TravelRequest


class MissingDepartureProvider:
    async def parse_itinerary(self, request: TravelRequest) -> ParseItineraryResponse:
        return ParseItineraryResponse(
            parsed_itinerary=ParsedItinerary(),
            raw_entities=[],
            warnings=["Departure airport was not explicitly identified."],
            confidence_score=0.8,
        )


@pytest.mark.asyncio
async def test_parse_use_case_adds_explicit_heathrow_return_departure() -> None:
    use_case = ParseItineraryUseCase(MissingDepartureProvider())

    response = await use_case.execute(
        TravelRequest(
            request_text="Day 14-15: London Heathrow, return and visa processing",
            default_country="United Kingdom",
        )
    )

    assert response.parsed_itinerary.departure is not None
    assert response.parsed_itinerary.departure.name == "Heathrow"
    assert response.parsed_itinerary.departure.role == "departure"
    assert "Departure airport was not explicitly identified." not in response.warnings
