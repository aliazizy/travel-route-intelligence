from typing import Any

from app.domain.models.itinerary import ItineraryStep
from app.domain.models.route import RouteSegment


class GeoJSONBuilder:
    def build(self, sequence: list[ItineraryStep], segments: list[RouteSegment]) -> dict[str, Any]:
        features: list[dict[str, Any]] = []

        for step in sequence:
            if step.latitude is None or step.longitude is None:
                continue
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [step.longitude, step.latitude],
                    },
                    "properties": {
                        "kind": "itinerary_step",
                        "sequence_index": step.sequence_index,
                        "day": step.day,
                        "name": step.name,
                        "step_type": step.step_type,
                        "role": step.role,
                        "confidence": step.confidence,
                        "editable": step.editable,
                        "locked": step.locked,
                        "warnings": step.warnings,
                    },
                }
            )

        for segment in segments:
            if not segment.geometry_geojson:
                continue
            features.append(
                {
                    "type": "Feature",
                    "geometry": segment.geometry_geojson,
                    "properties": {
                        "kind": "route_segment",
                        "from_sequence_index": segment.from_sequence_index,
                        "to_sequence_index": segment.to_sequence_index,
                        "distance_meters": segment.distance_meters,
                        "duration_seconds": segment.duration_seconds,
                        "provider": segment.provider,
                    },
                }
            )

        return {"type": "FeatureCollection", "features": features}
