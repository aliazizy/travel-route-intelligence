from app.domain.models.itinerary import ItineraryStep
from app.domain.models.route import RouteSegment
from app.domain.services.geojson_builder import GeoJSONBuilder


def test_geojson_builder_creates_point_and_line_features() -> None:
    sequence = [
        ItineraryStep(sequence_index=1, day=1, step_type="airport", name="A", latitude=1, longitude=2),
        ItineraryStep(sequence_index=2, day=1, step_type="hotel", name="B", latitude=3, longitude=4),
    ]
    segments = [
        RouteSegment(
            from_sequence_index=1,
            to_sequence_index=2,
            geometry_geojson={"type": "LineString", "coordinates": [[2, 1], [4, 3]]},
            provider="mock",
        )
    ]

    geojson = GeoJSONBuilder().build(sequence, segments)

    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 3
    assert geojson["features"][0]["properties"]["sequence_index"] == 1
    assert geojson["features"][2]["properties"]["kind"] == "route_segment"
