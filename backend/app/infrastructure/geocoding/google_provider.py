import re
from typing import Any

import httpx
import structlog

from app.domain.models.place import PlaceRequest, PlaceResolutionRequest, PlaceResolutionResponse, ResolvedPlace
from app.infrastructure.cache.base import CacheProvider
from app.infrastructure.geocoding.base import GeocoderProviderError

logger = structlog.get_logger(__name__)


class GoogleGeocoderProvider:
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"

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
        self.client = client or httpx.AsyncClient(timeout=10)

    async def resolve(self, request: PlaceResolutionRequest) -> PlaceResolutionResponse:
        resolved: list[ResolvedPlace] = []
        unresolved: list[PlaceRequest] = []
        warnings: list[str] = []

        for place in request.places:
            cache_key = self._cache_key(place)
            cached = await self.cache.get(cache_key)
            if cached is not None:
                logger.info("geocoding_cache_hit", provider="google", key=cache_key)
                response = PlaceResolutionResponse.model_validate(cached)
            else:
                logger.info("geocoding_cache_miss", provider="google", key=cache_key)
                response = await self._resolve_one(place)
                await self.cache.set(cache_key, response.model_dump(mode="json"), self.cache_ttl_seconds)

            resolved.extend(response.resolved_places)
            unresolved.extend(response.unresolved_places)
            warnings.extend(response.warnings)

        return PlaceResolutionResponse(
            resolved_places=resolved,
            unresolved_places=unresolved,
            warnings=warnings,
        )

    async def _resolve_one(self, place: PlaceRequest) -> PlaceResolutionResponse:
        query = self._query(place)
        try:
            response = await self.client.get(
                self.endpoint,
                params={"address": query, "key": self.api_key},
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise GeocoderProviderError("Google geocoding request failed.") from exc

        status = payload.get("status")
        if status == "ZERO_RESULTS":
            return PlaceResolutionResponse(
                unresolved_places=[place],
                warnings=[f"Could not resolve place '{place.raw_text}' with Google Geocoding."],
            )
        if status != "OK":
            logger.warning("google_geocoding_non_ok_status", status=status)
            raise GeocoderProviderError("Google Geocoding returned an error.")

        results = payload.get("results", [])
        if not results:
            return PlaceResolutionResponse(
                unresolved_places=[place],
                warnings=[f"Could not resolve place '{place.raw_text}' with Google Geocoding."],
            )

        primary = self._to_resolved_place(place, results[0], result_count=len(results))
        alternatives = [self._alternative(result) for result in results[1:4]]
        primary.alternatives = alternatives

        warnings: list[str] = []
        if self._should_warn_for_alternatives(place, results):
            warnings.append(
                f"Multiple possible matches found for '{place.raw_text}'. Review geocoding alternatives."
            )
        if primary.confidence < self._warning_threshold(place):
            warnings.append(f"Low-confidence geocoding result for '{place.raw_text}'.")

        return PlaceResolutionResponse(resolved_places=[primary], warnings=warnings)

    def _query(self, place: PlaceRequest) -> str:
        parts = [place.raw_text, place.city_hint, place.country_hint]
        return ", ".join(part for part in parts if part)

    def _cache_key(self, place: PlaceRequest) -> str:
        return "geocode:google:{place}:{country}:{city}".format(
            place=self._normalise(place.raw_text),
            country=self._normalise(place.country_hint or ""),
            city=self._normalise(place.city_hint or ""),
        )

    def _normalise(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "-"

    def _to_resolved_place(
        self,
        place: PlaceRequest,
        result: dict[str, Any],
        *,
        result_count: int,
    ) -> ResolvedPlace:
        location = result["geometry"]["location"]
        confidence = self._confidence(result, result_count)
        return ResolvedPlace(
            raw_text=place.raw_text,
            canonical_name=result.get("formatted_address") or place.raw_text,
            place_type=place.place_type,
            latitude=location["lat"],
            longitude=location["lng"],
            country=self._component(result, "country"),
            city=self._component(result, "locality")
            or self._component(result, "postal_town")
            or self._component(result, "administrative_area_level_2"),
            external_place_id=result.get("place_id"),
            provider="google",
            confidence=confidence,
        )

    def _alternative(self, result: dict[str, Any]) -> dict[str, Any]:
        location = result["geometry"]["location"]
        return {
            "canonical_name": result.get("formatted_address"),
            "latitude": location["lat"],
            "longitude": location["lng"],
            "external_place_id": result.get("place_id"),
            "confidence": self._confidence(result, result_count=2),
        }

    def _confidence(self, result: dict[str, Any], result_count: int) -> float:
        geometry = result.get("geometry", {})
        location_type = geometry.get("location_type")
        base = {
            "ROOFTOP": 0.95,
            "RANGE_INTERPOLATED": 0.82,
            "GEOMETRIC_CENTER": 0.78,
            "APPROXIMATE": 0.62,
        }.get(location_type, 0.65)
        if result.get("partial_match"):
            base -= 0.2
        if result_count > 1:
            base -= min(0.2, (result_count - 1) * 0.05)
        return round(max(0.0, min(base, 1.0)), 2)

    def _should_warn_for_alternatives(
        self,
        place: PlaceRequest,
        results: list[dict[str, Any]],
    ) -> bool:
        if len(results) <= 1:
            return False
        # Broad city/region/hotel-area searches often return several acceptable Google
        # candidates. Keep alternatives in the payload but avoid noisy consultant-facing warnings.
        return place.place_type not in {"city", "hotel"}

    def _warning_threshold(self, place: PlaceRequest) -> float:
        if place.place_type == "airport":
            return 0.75
        if place.place_type in {"city", "hotel"}:
            return 0.35
        return 0.7

    def _component(self, result: dict[str, Any], component_type: str) -> str | None:
        for component in result.get("address_components", []):
            if component_type in component.get("types", []):
                return component.get("long_name")
        return None
