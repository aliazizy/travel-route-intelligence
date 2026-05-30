from app.domain.models.itinerary import ParsedItinerary, ParsedPlaceRef
from app.domain.models.place import ResolvedPlace
from app.domain.services.sequence_builder import SequenceBuilder


def test_sequence_builder_keeps_low_confidence_on_step_not_global_warning() -> None:
    parsed = ParsedItinerary(
        activities=[ParsedPlaceRef(name="Seven Sisters Cliffs", place_type="activity")]
    )
    places = [
        ResolvedPlace(
            raw_text="Seven Sisters Cliffs",
            canonical_name="Seven Sisters Cliffs",
            place_type="activity",
            latitude=50.76,
            longitude=0.1475,
            provider="google",
            confidence=0.62,
        )
    ]

    result = SequenceBuilder().build(parsed, places)

    assert result.warnings == []
    assert result.sequence[0].warnings == ["Low-confidence geocoding result; review alternatives."]


def test_sequence_builder_does_not_warn_for_broad_low_confidence_city_anchor() -> None:
    parsed = ParsedItinerary(
        cities=[ParsedPlaceRef(name="Lake District", place_type="city")],
        hotels=[
            ParsedPlaceRef(
                name="Lake District hotel area",
                place_type="hotel",
                city_hint="Lake District",
            )
        ],
    )
    places = [
        ResolvedPlace(
            raw_text="Lake District hotel area",
            canonical_name="Lake District hotel area",
            place_type="hotel",
            latitude=54.4609,
            longitude=-3.0886,
            provider="google",
            confidence=0.42,
        )
    ]

    result = SequenceBuilder().build(parsed, places)

    assert result.warnings == []
    assert result.sequence[0].warnings == []
