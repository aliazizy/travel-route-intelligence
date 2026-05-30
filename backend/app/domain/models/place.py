from typing import Any

from pydantic import BaseModel, Field, field_validator


class PlaceRequest(BaseModel):
    raw_text: str
    place_type: str
    city_hint: str | None = None
    country_hint: str | None = None


class PlaceResolutionRequest(BaseModel):
    places: list[PlaceRequest] = Field(default_factory=list)


class ResolvedPlace(BaseModel):
    raw_text: str
    canonical_name: str
    place_type: str
    latitude: float
    longitude: float
    country: str | None = None
    city: str | None = None
    iata_code: str | None = None
    external_place_id: str | None = None
    provider: str
    confidence: float = Field(ge=0, le=1)
    alternatives: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("latitude")
    @classmethod
    def latitude_is_valid(cls, value: float) -> float:
        if not -90 <= value <= 90:
            msg = "Latitude must be between -90 and 90"
            raise ValueError(msg)
        return value

    @field_validator("longitude")
    @classmethod
    def longitude_is_valid(cls, value: float) -> float:
        if not -180 <= value <= 180:
            msg = "Longitude must be between -180 and 180"
            raise ValueError(msg)
        return value


class PlaceResolutionResponse(BaseModel):
    resolved_places: list[ResolvedPlace] = Field(default_factory=list)
    unresolved_places: list[PlaceRequest] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
