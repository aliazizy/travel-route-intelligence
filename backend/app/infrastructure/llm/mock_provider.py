import re

from app.domain.models.entity import TravelEntity
from app.domain.models.itinerary import ParsedItinerary, ParsedPlaceRef, ParseItineraryResponse, TravelRequest


class MockLLMProvider:
    """Deterministic parser for the MVP and regression tests."""

    _known_activities = [
        "Tower of London",
        "Westminster Abbey",
        "Westminster",
        "Windsor Castle",
        "Edinburgh Castle",
        "Royal Mile",
        "Cambridge University",
        "York Minster",
        "Lake District",
        "Giant’s Causeway",
        "Giant's Causeway",
        "Trinity College",
        "Stratford-upon-Avon",
        "Cotswolds",
        "Seven Sisters Cliffs",
        "British Museum",
        "Loch Ness",
        "Glenfinnan Viaduct",
        "Fort William",
        "Belfast City Hall",
        "St. Anne’s Cathedral",
        "Albert Clock",
        "Peace Wall",
        "Big Fish",
        "Eiffel Tower",
        "Louvre",
        "Seine cruise",
        "Oxford",
        "Bath",
        "Stonehenge",
        "Vatican",
        "Colosseum",
        "Uffizi",
        "gondola ride",
        "大英博物馆",
        "伦敦塔",
        "温莎城堡",
    ]

    async def parse_itinerary(self, request: TravelRequest) -> ParseItineraryResponse:
        text = request.request_text
        lower_text = text.lower()
        country = request.default_country
        warnings: list[str] = []
        entities: list[TravelEntity] = []

        group_match = re.search(r"(?P<size>\d+)\s*(?:pax|people|passengers|group|客户)?", text, re.I)
        if group_match:
            entities.append(
                TravelEntity(
                    text=group_match.group("size"),
                    entity_type="GROUP_SIZE",
                    start_char=group_match.start("size"),
                    end_char=group_match.end("size"),
                    confidence=0.95,
                    source="regex",
                )
            )

        arrival = self._airport_ref(text, lower_text, country, arrival=True)
        departure = self._airport_ref(text, lower_text, country, arrival=False)
        if "london airport" in lower_text:
            warnings.append(
                "London airport is ambiguous. Possible matches include Heathrow, Gatwick, Stansted, Luton and London City."
            )

        cities = self._city_refs(text, lower_text, country)
        hotels = self._hotel_refs(cities)
        activities = self._activity_refs(text, country)

        for ref in [arrival, departure, *cities, *hotels, *activities]:
            if ref is None:
                continue
            entity_type = "AIRPORT" if ref.place_type == "airport" else "CITY" if ref.place_type == "city" else "ATTRACTION"
            entities.append(
                TravelEntity(
                    text=ref.name,
                    entity_type=entity_type,
                    confidence=ref.confidence,
                    source="llm",
                )
            )

        parsed = ParsedItinerary(
            arrival=arrival,
            departure=departure,
            cities=cities,
            hotels=hotels,
            activities=activities,
            transport={"mode": "coach" if any(word in lower_text for word in ["coach", "private"]) else "driving"},
            constraints=["mock extraction; verify ambiguous places manually"],
        )

        if not arrival:
            warnings.append("Arrival airport was not explicitly identified.")
        if not departure:
            warnings.append("Departure airport was not explicitly identified.")
        if not cities:
            warnings.append("No overnight city was identified.")

        return ParseItineraryResponse(
            parsed_itinerary=parsed,
            raw_entities=entities,
            warnings=warnings,
            confidence_score=0.82 if warnings else 0.9,
        )

    def _airport_ref(
        self,
        text: str,
        lower_text: str,
        country: str | None,
        *,
        arrival: bool,
    ) -> ParsedPlaceRef | None:
        if arrival:
            if "heathrow" in lower_text or "希思罗" in text:
                return ParsedPlaceRef(
                    name="Heathrow",
                    place_type="airport",
                    country_hint=country or "United Kingdom",
                    role="arrival",
                    day=1,
                    locked=True,
                    confidence=0.92,
                )
            if "paris" in lower_text:
                return ParsedPlaceRef(name="Paris arrival airport", place_type="airport", role="arrival", day=1, locked=True, confidence=0.62)
            if "london airport" in lower_text:
                return ParsedPlaceRef(name="London airport", place_type="airport", country_hint=country, role="arrival", day=1, locked=True, confidence=0.45)
        else:
            if "edinburgh airport" in lower_text or "爱丁堡机场" in text:
                return ParsedPlaceRef(name="Edinburgh Airport", place_type="airport", country_hint=country or "United Kingdom", role="departure", locked=True, confidence=0.94)
            if "brussels airport" in lower_text:
                return ParsedPlaceRef(name="Brussels Airport", place_type="airport", role="departure", locked=True, confidence=0.9)
            if "london heathrow" in lower_text and "return" in lower_text:
                return ParsedPlaceRef(name="Heathrow", place_type="airport", country_hint=country or "United Kingdom", role="departure", locked=True, confidence=0.9)
            if "return from london" in lower_text:
                return ParsedPlaceRef(name="London airport", place_type="airport", country_hint=country, role="departure", locked=True, confidence=0.45)
        return None

    def _city_refs(self, text: str, lower_text: str, country: str | None) -> list[ParsedPlaceRef]:
        city_order = [
            ("London", "london", "伦敦"),
            ("Cambridge", "cambridge", ""),
            ("York", "york", ""),
            ("Lake District", "lake district", ""),
            ("Edinburgh", "edinburgh", "爱丁堡"),
            ("Scottish Highlands", "scottish highlands", ""),
            ("Glasgow", "glasgow", ""),
            ("Belfast", "belfast", ""),
            ("Dublin", "dublin", ""),
            ("Liverpool", "liverpool", ""),
            ("Manchester", "manchester", ""),
            ("Birmingham", "birmingham", ""),
            ("Stratford-upon-Avon", "stratford-upon-avon", ""),
            ("Cotswolds", "cotswolds", ""),
            ("Oxford", "oxford", ""),
            ("Windsor", "windsor", ""),
            ("Paris", "paris", ""),
            ("Brussels", "brussels", ""),
            ("Rome", "rome", ""),
            ("Florence", "florence", ""),
            ("Venice", "venice", ""),
        ]
        refs: list[ParsedPlaceRef] = []
        day = 1
        for city, token, zh_token in city_order:
            if token in lower_text or (zh_token and zh_token in text):
                nights = self._nights_near_city(lower_text, token)
                refs.append(
                    ParsedPlaceRef(
                        name=city,
                        place_type="city",
                        country_hint=country,
                        role="overnight_city",
                        day=day,
                        nights=nights,
                        confidence=0.86,
                    )
                )
                day += max(nights or 1, 1)
        return refs

    def _hotel_refs(self, cities: list[ParsedPlaceRef]) -> list[ParsedPlaceRef]:
        return [
            ParsedPlaceRef(
                name=f"{city.name} hotel area",
                place_type="hotel",
                city_hint=city.name,
                country_hint=city.country_hint,
                role="overnight",
                day=city.day,
                nights=city.nights,
                confidence=0.7,
                inferred=True,
            )
            for city in cities
        ]

    def _activity_refs(self, text: str, country: str | None) -> list[ParsedPlaceRef]:
        activities: list[ParsedPlaceRef] = []
        lower_text = text.lower()
        for name in self._known_activities:
            if name.lower() in lower_text or name in text:
                city_hint = self._activity_city_hint(name)
                activities.append(
                    ParsedPlaceRef(
                        name=name,
                        place_type="activity",
                        city_hint=city_hint,
                        country_hint=country,
                        confidence=0.82,
                    )
                )
        return activities

    def _activity_city_hint(self, name: str) -> str | None:
        lookup = {
            "Tower of London": "London",
            "Westminster": "London",
            "Westminster Abbey": "London",
            "Windsor Castle": "London",
            "Edinburgh Castle": "Edinburgh",
            "Royal Mile": "Edinburgh",
            "Cambridge University": "Cambridge",
            "York Minster": "York",
            "Lake District": "Lake District",
            "Giant’s Causeway": "Belfast",
            "Giant's Causeway": "Belfast",
            "Trinity College": "Dublin",
            "Stratford-upon-Avon": "Stratford-upon-Avon",
            "Cotswolds": "Cotswolds",
            "Oxford": "Oxford",
            "Seven Sisters Cliffs": "London",
            "British Museum": "London",
            "Loch Ness": "Scottish Highlands",
            "Glenfinnan Viaduct": "Scottish Highlands",
            "Fort William": "Scottish Highlands",
            "Belfast City Hall": "Belfast",
            "St. Anne’s Cathedral": "Belfast",
            "Albert Clock": "Belfast",
            "Peace Wall": "Belfast",
            "Big Fish": "Belfast",
            "大英博物馆": "London",
            "伦敦塔": "London",
            "温莎城堡": "London",
        }
        return lookup.get(name)

    def _nights_near_city(self, lower_text: str, city: str) -> int | None:
        match = re.search(rf"{city}.{{0,30}}?(?P<nights>\d+)\s*nights?", lower_text)
        if match:
            return int(match.group("nights"))
        words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        for word, number in words.items():
            if re.search(rf"{city}.{{0,30}}?{word}\s+nights?", lower_text):
                return number
        return None
