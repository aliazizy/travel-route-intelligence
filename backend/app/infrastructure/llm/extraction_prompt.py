EXTRACTION_SYSTEM_PROMPT = """
You are a travel itinerary information extraction engine.
Extract structured information from the user's free-text travel request.
Return only valid JSON matching the provided schema.

Rules:
- Do not invent latitude or longitude.
- Do not invent exact hotel names unless the user provided them.
- Do not fabricate dates, airports, restaurants, activities, or constraints.
- If a place is ambiguous, add a warning instead of resolving it.
- Infer only low-risk structure, such as city order or hotel area anchors.
- Mark inferred items with inferred=true.
- Preserve place names as candidate text for downstream geocoding.
- Use confidence scores between 0 and 1.
- Keep departure and arrival airports separate when possible.
""".strip()


EXTRACTION_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["parsed_itinerary", "raw_entities", "warnings", "confidence_score"],
    "properties": {
        "parsed_itinerary": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "arrival",
                "departure",
                "cities",
                "hotels",
                "activities",
                "restaurants",
                "transport",
                "constraints",
            ],
            "properties": {
                "arrival": {"anyOf": [{"$ref": "#/$defs/place_ref"}, {"type": "null"}]},
                "departure": {"anyOf": [{"$ref": "#/$defs/place_ref"}, {"type": "null"}]},
                "cities": {"type": "array", "items": {"$ref": "#/$defs/place_ref"}},
                "hotels": {"type": "array", "items": {"$ref": "#/$defs/place_ref"}},
                "activities": {"type": "array", "items": {"$ref": "#/$defs/place_ref"}},
                "restaurants": {"type": "array", "items": {"$ref": "#/$defs/place_ref"}},
                "transport": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["mode", "notes"],
                    "properties": {
                        "mode": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                        "notes": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "constraints": {"type": "array", "items": {"type": "string"}},
            },
        },
        "raw_entities": {"type": "array", "items": {"$ref": "#/$defs/entity"}},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "$defs": {
        "place_ref": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "name",
                "place_type",
                "city_hint",
                "country_hint",
                "role",
                "day",
                "nights",
                "locked",
                "confidence",
                "inferred",
            ],
            "properties": {
                "name": {"type": "string"},
                "place_type": {
                    "type": "string",
                    "enum": ["airport", "hotel", "activity", "restaurant", "transfer", "city", "custom"],
                },
                "city_hint": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "country_hint": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "role": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "day": {"anyOf": [{"type": "integer", "minimum": 1}, {"type": "null"}]},
                "nights": {"anyOf": [{"type": "integer", "minimum": 1}, {"type": "null"}]},
                "locked": {"type": "boolean"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "inferred": {"type": "boolean"},
            },
        },
        "entity": {
            "type": "object",
            "additionalProperties": False,
            "required": ["text", "entity_type", "start_char", "end_char", "confidence", "source"],
            "properties": {
                "text": {"type": "string"},
                "entity_type": {
                    "type": "string",
                    "enum": [
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
                    ],
                },
                "start_char": {"anyOf": [{"type": "integer", "minimum": 0}, {"type": "null"}]},
                "end_char": {"anyOf": [{"type": "integer", "minimum": 0}, {"type": "null"}]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "source": {"type": "string", "enum": ["llm", "gliner", "regex", "user", "system"]},
            },
        },
    },
}
