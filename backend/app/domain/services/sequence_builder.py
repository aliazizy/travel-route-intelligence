from app.domain.models.itinerary import BuildSequenceResponse, ItineraryStep, ParsedItinerary, ParsedPlaceRef
from app.domain.models.place import ResolvedPlace


class SequenceBuilder:
    def build(self, parsed: ParsedItinerary, places: list[ResolvedPlace]) -> BuildSequenceResponse:
        warnings: list[str] = []
        place_lookup = {place.raw_text.lower(): place for place in places}
        steps: list[ItineraryStep] = []

        def add_step(ref: ParsedPlaceRef, role: str | None = None, day: int | None = None) -> None:
            place = place_lookup.get(ref.name.lower())
            step_warnings: list[str] = []
            if not place:
                step_warnings.append("Location is unresolved.")
                warnings.append(f"Location '{ref.name}' is unresolved.")
            elif place.confidence < self._step_warning_threshold(ref.place_type):
                step_warnings.append("Low-confidence geocoding result; review alternatives.")

            steps.append(
                ItineraryStep(
                    sequence_index=len(steps) + 1,
                    day=day or ref.day,
                    step_type=ref.place_type,
                    name=place.canonical_name if place else ref.name,
                    latitude=place.latitude if place else None,
                    longitude=place.longitude if place else None,
                    role=role or ref.role,
                    confidence=min(ref.confidence, place.confidence) if place else ref.confidence,
                    locked=ref.locked,
                    editable=True,
                    warnings=step_warnings,
                )
            )

        if parsed.arrival:
            add_step(parsed.arrival, role="arrival", day=1)

        activity_queue = list(parsed.activities)
        for city in parsed.cities:
            hotel = self._hotel_for_city(parsed, city)
            city_day = city.day or max(len(steps), 1)
            if hotel:
                add_step(hotel, role="overnight", day=city_day)

            city_activities = [
                activity for activity in activity_queue if activity.city_hint == city.name or activity.city_hint is None
            ]
            for offset, activity in enumerate(city_activities):
                add_step(activity, role="visit", day=city_day + (offset % max(city.nights or 1, 1)))
                activity_queue.remove(activity)

            if hotel and (city.nights or 1) > 1:
                add_step(hotel, role="overnight_return", day=city_day + (city.nights or 1) - 1)

        for activity in activity_queue:
            add_step(activity, role="visit")

        if parsed.departure:
            add_step(parsed.departure, role="departure", day=self._last_day(steps))

        for index, step in enumerate(steps, start=1):
            step.sequence_index = index

        if not steps:
            warnings.append("No itinerary sequence could be built from the parsed request.")

        return BuildSequenceResponse(sequence=steps, warnings=warnings)

    def _hotel_for_city(self, parsed: ParsedItinerary, city: ParsedPlaceRef) -> ParsedPlaceRef | None:
        return next((hotel for hotel in parsed.hotels if hotel.city_hint == city.name), None)

    def _last_day(self, steps: list[ItineraryStep]) -> int | None:
        days = [step.day for step in steps if step.day is not None]
        return max(days) if days else None

    def _step_warning_threshold(self, step_type: str) -> float:
        if step_type in {"city", "hotel"}:
            return 0.35
        if step_type == "airport":
            return 0.75
        return 0.7
