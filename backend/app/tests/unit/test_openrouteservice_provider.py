import json

import httpx
import pytest

from app.core.config import Settings
from app.core.errors import AppError
from app.domain.models.itinerary import ItineraryStep
from app.domain.models.route import RouteCalculationRequest
from app.infrastructure.cache.in_memory import InMemoryTTLCache
from app.infrastructure.routing.base import RoutingProviderError
from app.infrastructure.routing.fallback_provider import FallbackRoutingProvider
from app.infrastructure.routing.mock_provider import MockRoutingProvider
from app.infrastructure.routing.openrouteservice_provider import OpenRouteServiceRoutingProvider
from app.infrastructure.routing.provider_factory import build_routing_provider


def ors_payload(distance: float = 1200.0, duration: float = 180.0) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"summary": {"distance": distance, "duration": duration}},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-0.4543, 51.47], [-0.1278, 51.5074]],
                },
            }
        ],
    }


def steps() -> list[ItineraryStep]:
    return [
        ItineraryStep(
            sequence_index=1,
            day=1,
            step_type="airport",
            name="Heathrow",
            latitude=51.47,
            longitude=-0.4543,
        ),
        ItineraryStep(
            sequence_index=2,
            day=1,
            step_type="hotel",
            name="Central London",
            latitude=51.5074,
            longitude=-0.1278,
        ),
    ]


@pytest.mark.asyncio
async def test_openrouteservice_provider_returns_geojson_segment() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        assert request.headers["Authorization"] == "ors-key"
        assert request.url.path.endswith("/driving-car/geojson")
        body = json.loads(request.content.decode())
        assert body["coordinates"][0] == [-0.4543, 51.47]
        return httpx.Response(200, json=ors_payload())

    provider = OpenRouteServiceRoutingProvider(
        api_key="ors-key",
        cache=InMemoryTTLCache(),
        cache_ttl_seconds=86400,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    result = await provider.calculate(RouteCalculationRequest(sequence=steps(), transport_mode="coach"))

    assert calls == 1
    assert result.total_distance_meters == 1200.0
    assert result.total_duration_seconds == 180.0
    assert result.route_segments[0].provider == "openrouteservice"
    assert result.route_segments[0].geometry_geojson["type"] == "LineString"


@pytest.mark.asyncio
async def test_openrouteservice_provider_uses_cache() -> None:
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=ors_payload())

    provider = OpenRouteServiceRoutingProvider(
        api_key="ors-key",
        cache=InMemoryTTLCache(),
        cache_ttl_seconds=86400,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    request = RouteCalculationRequest(sequence=steps(), transport_mode="driving")

    first = await provider.calculate(request)
    second = await provider.calculate(request)

    assert calls == 1
    assert first.route_segments[0].distance_meters == second.route_segments[0].distance_meters


@pytest.mark.asyncio
async def test_openrouteservice_provider_warns_for_missing_coordinates() -> None:
    provider = OpenRouteServiceRoutingProvider(
        api_key="ors-key",
        cache=InMemoryTTLCache(),
        cache_ttl_seconds=86400,
        client=httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200, json=ors_payload()))),
    )
    sequence = [
        steps()[0],
        ItineraryStep(sequence_index=2, step_type="custom", name="Unresolved"),
        steps()[1],
    ]

    result = await provider.calculate(RouteCalculationRequest(sequence=sequence, transport_mode="driving"))

    assert len(result.route_segments) == 1
    assert result.warnings == ["Some steps have no coordinates and were skipped during route calculation."]


def test_openrouteservice_factory_requires_api_key() -> None:
    with pytest.raises(AppError):
        build_routing_provider(
            Settings(routing_provider="openrouteservice", openrouteservice_api_key=None)
        )


class FailingRoutingProvider:
    async def calculate(self, request: RouteCalculationRequest):
        raise RoutingProviderError("Provider failed")


@pytest.mark.asyncio
async def test_fallback_routing_uses_mock_when_primary_fails() -> None:
    provider = FallbackRoutingProvider(
        primary=FailingRoutingProvider(),
        fallback=MockRoutingProvider(),
    )

    result = await provider.calculate(RouteCalculationRequest(sequence=steps(), transport_mode="driving"))

    assert result.route_segments[0].provider == "mock"
    assert result.warnings[0] == "Primary routing provider failed; used fallback mock routing for this request."
