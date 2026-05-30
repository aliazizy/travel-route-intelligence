from math import asin, cos, radians, sin, sqrt

from app.domain.models.itinerary import ItineraryStep
from app.domain.models.route import RouteCalculationRequest, RouteCalculationResponse, RouteSegment


class MockRoutingProvider:
    async def calculate(self, request: RouteCalculationRequest) -> RouteCalculationResponse:
        segments: list[RouteSegment] = []
        total_distance = 0.0
        total_duration = 0.0
        warnings: list[str] = []

        routable_steps = [step for step in request.sequence if step.latitude is not None and step.longitude is not None]
        for origin, destination in zip(routable_steps, routable_steps[1:], strict=False):
            distance = self._distance_meters(origin, destination)
            duration = distance / 13.8 if request.transport_mode in {"driving", "coach"} else distance / 1.4
            total_distance += distance
            total_duration += duration
            segments.append(
                RouteSegment(
                    from_sequence_index=origin.sequence_index,
                    to_sequence_index=destination.sequence_index,
                    distance_meters=round(distance, 1),
                    duration_seconds=round(duration, 1),
                    geometry_geojson={
                        "type": "LineString",
                        "coordinates": [
                            [origin.longitude, origin.latitude],
                            [destination.longitude, destination.latitude],
                        ],
                    },
                    provider="mock",
                )
            )

        if len(routable_steps) < len(request.sequence):
            warnings.append("Some steps have no coordinates and were skipped during route calculation.")

        return RouteCalculationResponse(
            route_segments=segments,
            total_distance_meters=round(total_distance, 1),
            total_duration_seconds=round(total_duration, 1),
            warnings=warnings,
        )

    def _distance_meters(self, origin: ItineraryStep, destination: ItineraryStep) -> float:
        lat1 = radians(origin.latitude or 0)
        lon1 = radians(origin.longitude or 0)
        lat2 = radians(destination.latitude or 0)
        lon2 = radians(destination.longitude or 0)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 6_371_000 * 2 * asin(sqrt(a))
