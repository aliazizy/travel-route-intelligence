from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app


app.dependency_overrides[get_settings] = lambda: Settings(llm_provider="mock")
client = TestClient(app)


def test_full_process_builds_uk_multi_city_route() -> None:
    response = client.post(
        "/api/v1/workflows/full-process",
        json={
            "request_text": (
                "Group of 25 arrives at Heathrow on 10 September. Stay 3 nights in London. "
                "Visit Tower of London, Westminster Abbey and Windsor Castle. Then travel to "
                "Edinburgh for 2 nights, visit Edinburgh Castle and Royal Mile, and fly back "
                "from Edinburgh Airport."
            ),
            "default_country": "United Kingdom",
            "language": "en",
            "client_context": {"group_size": 25, "travel_style": "private coach"},
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["parsed_itinerary"]["arrival"]["name"] == "Heathrow"
    assert len(body["resolved_places"]) >= 8
    assert body["sequence"][0]["role"] == "arrival"
    assert body["sequence"][-1]["role"] == "departure"
    assert len(body["route_segments"]) == len(body["sequence"]) - 1
    assert body["geojson"]["type"] == "FeatureCollection"
    assert body["confidence_summary"]["overall"] > 0.7


def test_full_process_flags_ambiguous_london_airport() -> None:
    response = client.post(
        "/api/v1/workflows/full-process",
        json={
            "request_text": (
                "Arrive London airport, 4 nights UK, include Oxford, Bath and Stonehenge, "
                "return from London."
            ),
            "default_country": "United Kingdom",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert any("London airport is ambiguous" in warning for warning in body["warnings"])
    assert any(place["raw_text"] == "London airport" for place in body["resolved_places"])
    ambiguous_place = next(place for place in body["resolved_places"] if place["raw_text"] == "London airport")
    assert ambiguous_place["confidence"] < 0.7
    assert len(ambiguous_place["alternatives"]) >= 2


def test_full_process_handles_15_day_uk_ireland_panoramic_itinerary() -> None:
    request_text = """
    15-Day UK & Ireland Panoramic Itinerary – Summary
    Travel Dates:
        Day 1–2: London, Cambridge, York
        Day 3–4: Lake District, Edinburgh, Scottish Highlands, Glasgow
        Day 5–6: Ferry to Belfast, Giant’s Causeway, Dublin
        Day 7–9: Ferry to Liverpool, Manchester, Birmingham
        Day 10–12: Stratford-upon-Avon, Cotswolds, Oxford, Windsor, London, Seven Sisters Cliffs
        Day 13: Free day in London
        Day 14–15: London Heathrow, return and visa processing
    25 adults, 01/05/2026, uk citizens, city tax and insurance are excluded.
    Accommodation: 4-star hotels, twin rooms with daily breakfast included 13 nights in hotel,
    1 overnight on the return flight.
    Transport: Private coach throughout. Ferry crossings: Cairnryan to Belfast,
    Dublin to Holyhead. Domestic travel by coach.
    Key Highlights by Region: England Cambridge University York Minster, city walls,
    Shambles, Lake District cruise and vintage steam train, Manchester and Liverpool,
    Stratford-upon-Avon, Oxford, Windsor Castle, London Parliament, Big Ben, Thames Cruise,
    Buckingham Palace, British Museum, Seven Sisters Cliffs. Scotland Edinburgh Castle,
    Holyrood Palace, Royal Mile, Loch Ness, Glenfinnan Viaduct, Fort William, Glasgow.
    Northern Ireland Giant’s Causeway, Belfast City Hall, St. Anne’s Cathedral, Albert Clock,
    Peace Wall, Big Fish. Ireland Dublin Trinity College, Phoenix Park, Merrion Square.
    Visa Notes: Passport and boarding passes must be returned after travel for visa cancellation.
    """

    response = client.post(
        "/api/v1/workflows/full-process",
        json={
            "request_text": request_text,
            "default_country": "United Kingdom",
            "language": "en",
            "client_context": {
                "group_size": 25,
                "travel_style": "private coach",
                "hotel_category": "4-star",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    parsed_city_names = [city["name"] for city in body["parsed_itinerary"]["cities"]]
    sequence_names = [step["name"] for step in body["sequence"]]
    resolved_raw_names = [place["raw_text"] for place in body["resolved_places"]]

    assert body["parsed_itinerary"]["arrival"]["name"] == "Heathrow"
    assert body["parsed_itinerary"]["departure"]["name"] == "Heathrow"
    assert body["parsed_itinerary"]["transport"]["mode"] == "coach"
    assert body["sequence"][0]["role"] == "arrival"
    assert body["sequence"][-1]["role"] == "departure"
    assert body["geojson"]["type"] == "FeatureCollection"
    assert len(body["route_segments"]) == len(body["sequence"]) - 1

    for city in [
        "London",
        "Cambridge",
        "York",
        "Lake District",
        "Edinburgh",
        "Scottish Highlands",
        "Glasgow",
        "Belfast",
        "Dublin",
        "Liverpool",
        "Manchester",
        "Birmingham",
        "Stratford-upon-Avon",
        "Cotswolds",
        "Oxford",
        "Windsor",
    ]:
        assert city in parsed_city_names

    for place in [
        "Cambridge University",
        "York Minster",
        "Giant’s Causeway",
        "Trinity College",
        "Seven Sisters Cliffs",
        "British Museum",
        "Loch Ness",
        "Glenfinnan Viaduct",
        "Belfast City Hall",
    ]:
        assert place in resolved_raw_names

    assert any("Seven Sisters Cliffs" in name for name in sequence_names)
    assert body["confidence_summary"]["overall"] > 0.7
