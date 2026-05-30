import hashlib
import json

import httpx
import structlog

from app.domain.models.itinerary import ItineraryStep
from app.domain.models.route import RouteCalculationRequest, RouteCalculationResponse, RouteSegment
from app.infrastructure.cache.base import CacheProvider
from app.infrastructure.routing.base import RoutingProviderError

logger = structlog.get_logger(__name__)


class OpenRouteServiceRoutingProvider:
    endpoint = "https://api.openrouteservice.org/v2/directions/{profile}/geojson"

    def __init__(
        self,
        *,
        api_key: str,
        cache: CacheProvider,
        cache_ttl_seconds: int,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.cache = cache
        self.cache_ttl_seconds = cache_ttl_seconds
        self.client = client or httpx.AsyncClient(timeout=20)

    async def calculate(self, request: RouteCalculationRequest) -> RouteCalculationResponse:
        segments: list[RouteSegment] = []
        warnings: list[str] = []
        total_distance = 0.0
        total_duration = 0.0

        routable_steps = [step for step in request.sequence if self._has_coordinates(step)]
        if len(routable_steps) < len(request.sequence):
            warnings.append("Some steps have no coordinates and were skipped during route calculation.")

        for origin, destination in zip(routable_steps, routable_steps[1:], strict=False):
            cache_key = self._cache_key(request.transport_mode, origin, destination)
            cached = await self.cache.get(cache_key)
            if cached is not None:
                logger.info("routing_cache_hit", provider="openrouteservice", key=cache_key)
                segment = RouteSegment.model_validate(cached)
            else:
                logger.info("routing_cache_miss", provider="openrouteservice", key=cache_key)
                segment = await self._calculate_segment(request.transport_mode, origin, destination)
                await self.cache.set(cache_key, segment.model_dump(mode="json"), self.cache_ttl_seconds)

            total_distance += segment.distance_meters or 0
            total_duration += segment.duration_seconds or 0
            segments.append(segment)

        return RouteCalculationResponse(
            route_segments=segments,
            total_distance_meters=round(total_distance, 1),
            total_duration_seconds=round(total_duration, 1),
            warnings=warnings,
        )

    async def _calculate_segment(
        self,
        transport_mode: str,
        origin: ItineraryStep,
        destination: ItineraryStep,
    ) -> RouteSegment:
        profile = self._profile(transport_mode)
        body = {
            "coordinates": [
                [origin.longitude, origin.latitude],
                [destination.longitude, destination.latitude],
            ]
        }
        try:
            response = await self.client.post(
                self.endpoint.format(profile=profile),
                headers={
                    "Authorization": self.api_key,
                    "Content-Type": "application/json",
                    "Accept": "application/json, application/geo+json",
                },
                json=body,
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise RoutingProviderError("OpenRouteService routing request failed.") from exc

        features = payload.get("features") or []
        if not features:
            raise RoutingProviderError("OpenRouteService returned no route features.")

        feature = features[0]
        summary = feature.get("properties", {}).get("summary", {})
        geometry = feature.get("geometry")
        if not geometry:
            raise RoutingProviderError("OpenRouteService returned no route geometry.")

        return RouteSegment(
            from_sequence_index=origin.sequence_index,
            to_sequence_index=destination.sequence_index,
            distance_meters=summary.get("distance"),
            duration_seconds=summary.get("duration"),
            geometry_geojson=geometry,
            provider="openrouteservice",
        )

    def _profile(self, transport_mode: str) -> str:
        if transport_mode == "walking":
            return "foot-walking"
        # ORS does not have a distinct coach profile; heavy-vehicle can be introduced later.
        return "driving-car"

    def _has_coordinates(self, step: ItineraryStep) -> bool:
        return step.latitude is not None and step.longitude is not None

    def _cache_key(self, transport_mode: str, origin: ItineraryStep, destination: ItineraryStep) -> str:
        payload = {
            "mode": transport_mode,
            "origin": [round(origin.latitude or 0, 6), round(origin.longitude or 0, 6)],
            "destination": [round(destination.latitude or 0, 6), round(destination.longitude or 0, 6)],
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        return f"route:openrouteservice:{transport_mode}:{digest}"
