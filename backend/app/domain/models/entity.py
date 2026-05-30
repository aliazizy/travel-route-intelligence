from typing import Literal

from pydantic import BaseModel, Field


EntityType = Literal[
    "AIRPORT",
    "IATA_CODE",
    "CITY",
    "COUNTRY",
    "HOTEL",
    "HOTEL_AREA",
    "ATTRACTION",
    "RESTAURANT",
    "DATE",
    "TIME",
    "DURATION",
    "NIGHT_COUNT",
    "GROUP_SIZE",
    "TRANSPORT_MODE",
    "CONSTRAINT",
    "SEQUENCE_HINT",
]

EntitySource = Literal["llm", "gliner", "regex", "user", "system"]


class TravelEntity(BaseModel):
    text: str
    entity_type: EntityType
    start_char: int | None = None
    end_char: int | None = None
    confidence: float = Field(ge=0, le=1)
    source: EntitySource
