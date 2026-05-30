from typing import Any, Literal

from pydantic import BaseModel, Field

from app.domain.models.entity import TravelEntity


StepType = Literal["airport", "hotel", "activity", "restaurant", "transfer", "city", "custom"]


class TravelRequest(BaseModel):
    request_text: str = Field(min_length=3, max_length=20_000)
    default_country: str | None = None
    language: str = "en"
    client_context: dict[str, Any] = Field(default_factory=dict)


class ParsedPlaceRef(BaseModel):
    name: str
    place_type: StepType
    city_hint: str | None = None
    country_hint: str | None = None
    role: str | None = None
    day: int | None = None
    nights: int | None = None
    locked: bool = False
    confidence: float = Field(default=0.8, ge=0, le=1)
    inferred: bool = False


class ParsedItinerary(BaseModel):
    arrival: ParsedPlaceRef | None = None
    departure: ParsedPlaceRef | None = None
    cities: list[ParsedPlaceRef] = Field(default_factory=list)
    hotels: list[ParsedPlaceRef] = Field(default_factory=list)
    activities: list[ParsedPlaceRef] = Field(default_factory=list)
    restaurants: list[ParsedPlaceRef] = Field(default_factory=list)
    transport: dict[str, Any] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)


class ParseItineraryResponse(BaseModel):
    parsed_itinerary: ParsedItinerary
    raw_entities: list[TravelEntity] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0, le=1)


class ItineraryStep(BaseModel):
    sequence_index: int
    day: int | None = None
    step_type: StepType
    name: str
    latitude: float | None = None
    longitude: float | None = None
    role: str | None = None
    duration_minutes: int | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    locked: bool = False
    editable: bool = True
    warnings: list[str] = Field(default_factory=list)


class BuildSequenceRequest(BaseModel):
    parsed_itinerary: ParsedItinerary
    resolved_places: list[Any] = Field(default_factory=list)


class BuildSequenceResponse(BaseModel):
    sequence: list[ItineraryStep]
    warnings: list[str] = Field(default_factory=list)
