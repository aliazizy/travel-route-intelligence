import pytest

from app.application.use_cases.resolve_places import ResolvePlacesUseCase
from app.domain.models.itinerary import ParsedItinerary, ParsedPlaceRef
from app.domain.models.place import PlaceResolutionRequest, PlaceResolutionResponse


class RecordingGeocoder:
    def __init__(self) -> None:
        self.request: PlaceResolutionRequest | None = None

    async def resolve(self, request: PlaceResolutionRequest) -> PlaceResolutionResponse:
        self.request = request
        return PlaceResolutionResponse()


@pytest.mark.asyncio
async def test_resolve_places_deduplicates_repeated_place_names() -> None:
    geocoder = RecordingGeocoder()
    use_case = ResolvePlacesUseCase(geocoder)

    await use_case.execute(
        ParsedItinerary(
            cities=[ParsedPlaceRef(name="Oxford", place_type="city")],
            activities=[ParsedPlaceRef(name="Oxford", place_type="activity")],
            hotels=[ParsedPlaceRef(name="Oxford hotel area", place_type="hotel")],
        )
    )

    assert geocoder.request is not None
    assert [place.raw_text for place in geocoder.request.places] == ["Oxford", "Oxford hotel area"]
