import structlog

from app.domain.models.place import PlaceResolutionRequest, PlaceResolutionResponse
from app.infrastructure.geocoding.base import GeocoderProvider, GeocoderProviderError

logger = structlog.get_logger(__name__)


class FallbackGeocoderProvider:
    def __init__(self, primary: GeocoderProvider, fallback: GeocoderProvider) -> None:
        self.primary = primary
        self.fallback = fallback

    async def resolve(self, request: PlaceResolutionRequest) -> PlaceResolutionResponse:
        try:
            return await self.primary.resolve(request)
        except GeocoderProviderError:
            logger.warning("geocoder_primary_failed_using_fallback")
            response = await self.fallback.resolve(request)
            return PlaceResolutionResponse(
                resolved_places=response.resolved_places,
                unresolved_places=response.unresolved_places,
                warnings=[
                    "Primary geocoder failed; used fallback mock geocoder for this request.",
                    *response.warnings,
                ],
            )
