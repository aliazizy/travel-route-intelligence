from app.core.config import Settings
from app.core.errors import AppError, ErrorCode
from app.infrastructure.cache.in_memory import InMemoryTTLCache
from app.infrastructure.geocoding.base import GeocoderProvider
from app.infrastructure.geocoding.fallback_provider import FallbackGeocoderProvider
from app.infrastructure.geocoding.google_provider import GoogleGeocoderProvider
from app.infrastructure.geocoding.mock_provider import MockGeocoderProvider


_geocoding_cache = InMemoryTTLCache()


def build_geocoder_provider(settings: Settings) -> GeocoderProvider:
    if settings.geocoder_provider == "mock":
        return MockGeocoderProvider()

    if settings.geocoder_provider == "google":
        if not settings.google_maps_api_key:
            raise AppError(
                ErrorCode.geocoding_failed,
                "Google geocoder is selected but GOOGLE_MAPS_API_KEY is missing.",
                details={"missing": ["GOOGLE_MAPS_API_KEY"]},
                status_code=500,
            )
        return FallbackGeocoderProvider(
            primary=GoogleGeocoderProvider(
                api_key=settings.google_maps_api_key,
                cache=_geocoding_cache,
                cache_ttl_seconds=settings.geocoding_cache_ttl_seconds,
            ),
            fallback=MockGeocoderProvider(),
        )

    raise AppError(
        ErrorCode.geocoding_failed,
        f"Geocoder provider '{settings.geocoder_provider}' is not implemented yet.",
        recoverable=True,
        status_code=501,
    )
