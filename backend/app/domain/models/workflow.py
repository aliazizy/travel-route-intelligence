from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.models.entity import TravelEntity
from app.domain.models.itinerary import ParsedItinerary, ItineraryStep
from app.domain.models.place import ResolvedPlace
from app.domain.models.route import RouteSegment


class ConfidenceSummary(BaseModel):
    overall: float = Field(ge=0, le=1)
    parsing: float = Field(ge=0, le=1)
    geocoding: float = Field(ge=0, le=1)
    sequencing: float = Field(ge=0, le=1)


class FullProcessResponse(BaseModel):
    request_id: UUID
    parsed_itinerary: ParsedItinerary
    entities: list[TravelEntity]
    resolved_places: list[ResolvedPlace]
    unresolved_places: list[dict[str, Any]] = Field(default_factory=list)
    sequence: list[ItineraryStep]
    route_segments: list[RouteSegment]
    geojson: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)
    confidence_summary: ConfidenceSummary
