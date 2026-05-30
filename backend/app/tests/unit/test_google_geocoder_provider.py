import json

import httpx
import pytest

from app.core.config import Settings
from app.core.errors import AppError
from app.domain.models.place import PlaceRequest, PlaceResolutionRequest
from app.infrastructure.cache.in_memory import InMemoryTTLCache
from app.infrastructure.geocoding.base import GeocoderProviderError
from app.infrastructure.geocoding.fallback_provider import FallbackGeocoderProvider
from app.infrastructure.geocoding.google_provider import GoogleGeocoderProvider
from app.infrastructure.geocoding.mock_provider import MockGeocoderProvider
from app.infrastructure.geocoding.provider_factory import build_geocoder_provider


def google_payload(*results: dict) -> dict:
    return {"status": "OK", "results": list(results)}


def google_result(
    *,
    formatted_address: str,
    place_id: str,
    lat: float,
    lng: float,
    location_type: str = "ROOFTOP",
    city: str = "London",
    country: str = "United Kingdom",
    partial_match: bool = False,
) -> dict:
    return {
        "formatted_address": formatted_address,
        "place_id": place_id,
        "partial_match": partial_match,
        "geometry": {
            "location": {"lat": lat, "lng": lng},
            "location_type": location_type,
        },
        "address_components": [
            {"long_name": city, "types": ["locality"]},
            {"long_name": country, "types": ["country"]},
        ],
    }


@pytest.mark.asyncio
async def test_google_geocoder_resolves_place_and_returns_alternatives() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        assert request.url.params["key"] == "test-key"
        return httpx.Response(
            200,
            json=google_payload(
                google_result(
                    formatted_address="London Heathrow Airport, Longford TW6, UK",
                    place_id="heathrow",
                    lat=51.47,
                    lng=-0.4543,
                ),
                google_result(
                    formatted_address="Heathrow Terminal 5, Longford TW6, UK",
                    place_id="heathrow-t5",
                    lat=51.4722,
                    lng=-0.4899,
                    location_type="GEOMETRIC_CENTER",
                ),
            ),
        )

    provider = GoogleGeocoderProvider(
        api_key="test-key",
        cache=InMemoryTTLCache(),
        cache_ttl_seconds=86400,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    result = await provider.resolve(
        PlaceResolutionRequest(
            places=[
                PlaceRequest(
                    raw_text="Heathrow",
                    place_type="airport",
                    city_hint="London",
                    country_hint="United Kingdom",
                )
            ]
        )
    )

    assert calls == 1
    assert result.resolved_places[0].provider == "google"
    assert result.resolved_places[0].external_place_id == "heathrow"
    assert result.resolved_places[0].confidence == 0.9
    assert len(result.resolved_places[0].alternatives) == 1
    assert any("Multiple possible matches" in warning for warning in result.warnings)


@pytest.mark.asyncio
async def test_google_geocoder_uses_cache_for_repeated_place() -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            json=google_payload(
                google_result(
                    formatted_address="Tower of London, London EC3N 4AB, UK",
                    place_id="tower",
                    lat=51.5081,
                    lng=-0.0759,
                )
            ),
        )

    provider = GoogleGeocoderProvider(
        api_key="test-key",
        cache=InMemoryTTLCache(),
        cache_ttl_seconds=86400,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    request = PlaceResolutionRequest(
        places=[PlaceRequest(raw_text="Tower of London", place_type="activity", city_hint="London")]
    )

    first = await provider.resolve(request)
    second = await provider.resolve(request)

    assert calls == 1
    assert json.dumps(first.model_dump(mode="json"), sort_keys=True) == json.dumps(
        second.model_dump(mode="json"),
        sort_keys=True,
    )


@pytest.mark.asyncio
async def test_google_geocoder_suppresses_broad_city_area_warning_noise() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=google_payload(
                google_result(
                    formatted_address="Lake District National Park, United Kingdom",
                    place_id="lake-district",
                    lat=54.4609,
                    lng=-3.0886,
                    location_type="APPROXIMATE",
                    city="Cumbria",
                ),
                google_result(
                    formatted_address="Lake District, Cumbria, United Kingdom",
                    place_id="lake-district-alt",
                    lat=54.5,
                    lng=-3.1,
                    location_type="APPROXIMATE",
                    city="Cumbria",
                ),
            ),
        )

    provider = GoogleGeocoderProvider(
        api_key="test-key",
        cache=InMemoryTTLCache(),
        cache_ttl_seconds=86400,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    result = await provider.resolve(
        PlaceResolutionRequest(
            places=[
                PlaceRequest(
                    raw_text="Lake District",
                    place_type="city",
                    country_hint="United Kingdom",
                )
            ]
        )
    )

    assert result.resolved_places[0].confidence == 0.57
    assert result.warnings == []


def test_google_provider_factory_requires_api_key() -> None:
    with pytest.raises(AppError):
        build_geocoder_provider(Settings(geocoder_provider="google", google_maps_api_key=None))


class FailingGeocoder:
    async def resolve(self, request: PlaceResolutionRequest):
        raise GeocoderProviderError("Provider failed")


@pytest.mark.asyncio
async def test_fallback_geocoder_uses_mock_when_primary_fails() -> None:
    provider = FallbackGeocoderProvider(primary=FailingGeocoder(), fallback=MockGeocoderProvider())

    result = await provider.resolve(
        PlaceResolutionRequest(
            places=[
                PlaceRequest(
                    raw_text="Heathrow",
                    place_type="airport",
                    country_hint="United Kingdom",
                )
            ]
        )
    )

    assert result.resolved_places[0].canonical_name == "London Heathrow Airport"
    assert result.warnings[0] == "Primary geocoder failed; used fallback mock geocoder for this request."
