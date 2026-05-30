from app.core.errors import AppError, ErrorCode
from app.domain.models.itinerary import ParsedItinerary, ParsedPlaceRef
from app.domain.models.place import PlaceRequest, PlaceResolutionRequest, PlaceResolutionResponse
from app.infrastructure.geocoding.base import GeocoderProvider, GeocoderProviderError


class ResolvePlacesUseCase:
    def __init__(self, provider: GeocoderProvider) -> None:
        self.provider = provider

    async def execute(self, parsed: ParsedItinerary) -> PlaceResolutionResponse:
        refs = self._refs_from_itinerary(parsed)
        request = PlaceResolutionRequest(
            places=[
                PlaceRequest(
                    raw_text=ref.name,
                    place_type=ref.place_type,
                    city_hint=ref.city_hint,
                    country_hint=ref.country_hint,
                )
                for ref in refs
            ]
        )
        try:
            return await self.provider.resolve(request)
        except GeocoderProviderError as exc:
            raise AppError(
                ErrorCode.geocoding_failed,
                str(exc),
                recoverable=True,
                status_code=502,
            ) from exc

    def _refs_from_itinerary(self, parsed: ParsedItinerary) -> list[ParsedPlaceRef]:
        refs: list[ParsedPlaceRef] = []
        for ref in [parsed.arrival, parsed.departure]:
            if ref:
                refs.append(ref)
        refs.extend(parsed.cities)
        refs.extend(parsed.hotels)
        refs.extend(parsed.activities)
        refs.extend(parsed.restaurants)

        unique_refs: list[ParsedPlaceRef] = []
        seen_names: set[str] = set()
        for ref in refs:
            key = ref.name.strip().lower()
            if key in seen_names:
                continue
            seen_names.add(key)
            unique_refs.append(ref)
        return unique_refs
