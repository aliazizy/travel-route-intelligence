from typing import Any, Literal

from pydantic import BaseModel, Field

from app.domain.models.itinerary import ItineraryStep


TransportMode = Literal["driving", "walking", "coach", "public_transport"]


class RouteCalculationRequest(BaseModel):
    sequence: list[ItineraryStep] = Field(default_factory=list)
    transport_mode: TransportMode = "driving"


class RouteSegment(BaseModel):
    from_sequence_index: int
    to_sequence_index: int
    distance_meters: float | None = None
    duration_seconds: float | None = None
    polyline: str | None = None
    geometry_geojson: dict[str, Any] | None = None
    provider: str | None = None
    warnings: list[str] = Field(default_factory=list)


class RouteCalculationResponse(BaseModel):
    route_segments: list[RouteSegment]
    total_distance_meters: float = 0
    total_duration_seconds: float = 0
    warnings: list[str] = Field(default_factory=list)
