from app.domain.models.place import PlaceRequest, PlaceResolutionRequest, PlaceResolutionResponse, ResolvedPlace


class MockGeocoderProvider:
    _places = {
        "heathrow": ("London Heathrow Airport", "airport", 51.4700, -0.4543, "London", "United Kingdom", "LHR", 0.98),
        "london heathrow airport": ("London Heathrow Airport", "airport", 51.4700, -0.4543, "London", "United Kingdom", "LHR", 0.98),
        "edinburgh airport": ("Edinburgh Airport", "airport", 55.9500, -3.3725, "Edinburgh", "United Kingdom", "EDI", 0.97),
        "london": ("London", "city", 51.5074, -0.1278, "London", "United Kingdom", None, 0.92),
        "cambridge": ("Cambridge", "city", 52.2053, 0.1218, "Cambridge", "United Kingdom", None, 0.9),
        "york": ("York", "city", 53.9590, -1.0815, "York", "United Kingdom", None, 0.9),
        "lake district": ("Lake District National Park", "city", 54.4609, -3.0886, "Cumbria", "United Kingdom", None, 0.86),
        "edinburgh": ("Edinburgh", "city", 55.9533, -3.1883, "Edinburgh", "United Kingdom", None, 0.92),
        "scottish highlands": ("Scottish Highlands", "city", 57.1200, -4.7100, "Highlands", "United Kingdom", None, 0.82),
        "glasgow": ("Glasgow", "city", 55.8642, -4.2518, "Glasgow", "United Kingdom", None, 0.9),
        "belfast": ("Belfast", "city", 54.5973, -5.9301, "Belfast", "United Kingdom", None, 0.9),
        "dublin": ("Dublin", "city", 53.3498, -6.2603, "Dublin", "Ireland", None, 0.9),
        "liverpool": ("Liverpool", "city", 53.4084, -2.9916, "Liverpool", "United Kingdom", None, 0.9),
        "manchester": ("Manchester", "city", 53.4808, -2.2426, "Manchester", "United Kingdom", None, 0.9),
        "birmingham": ("Birmingham", "city", 52.4862, -1.8904, "Birmingham", "United Kingdom", None, 0.9),
        "stratford-upon-avon": ("Stratford-upon-Avon", "city", 52.1917, -1.7083, "Stratford-upon-Avon", "United Kingdom", None, 0.88),
        "cotswolds": ("Cotswolds", "city", 51.8330, -1.8433, "Cotswolds", "United Kingdom", None, 0.84),
        "oxford": ("Oxford", "city", 51.7520, -1.2577, "Oxford", "United Kingdom", None, 0.9),
        "windsor": ("Windsor", "city", 51.4816, -0.6136, "Windsor", "United Kingdom", None, 0.9),
        "london hotel area": ("Central London hotel area", "hotel", 51.5074, -0.1278, "London", "United Kingdom", None, 0.76),
        "cambridge hotel area": ("Cambridge hotel area", "hotel", 52.2053, 0.1218, "Cambridge", "United Kingdom", None, 0.72),
        "york hotel area": ("York hotel area", "hotel", 53.9590, -1.0815, "York", "United Kingdom", None, 0.72),
        "lake district hotel area": ("Lake District hotel area", "hotel", 54.4609, -3.0886, "Cumbria", "United Kingdom", None, 0.72),
        "edinburgh hotel area": ("Edinburgh Old Town hotel area", "hotel", 55.9486, -3.1999, "Edinburgh", "United Kingdom", None, 0.76),
        "scottish highlands hotel area": ("Scottish Highlands hotel area", "hotel", 57.1200, -4.7100, "Highlands", "United Kingdom", None, 0.72),
        "glasgow hotel area": ("Glasgow hotel area", "hotel", 55.8642, -4.2518, "Glasgow", "United Kingdom", None, 0.72),
        "belfast hotel area": ("Belfast hotel area", "hotel", 54.5973, -5.9301, "Belfast", "United Kingdom", None, 0.72),
        "dublin hotel area": ("Dublin hotel area", "hotel", 53.3498, -6.2603, "Dublin", "Ireland", None, 0.72),
        "liverpool hotel area": ("Liverpool hotel area", "hotel", 53.4084, -2.9916, "Liverpool", "United Kingdom", None, 0.72),
        "manchester hotel area": ("Manchester hotel area", "hotel", 53.4808, -2.2426, "Manchester", "United Kingdom", None, 0.72),
        "birmingham hotel area": ("Birmingham hotel area", "hotel", 52.4862, -1.8904, "Birmingham", "United Kingdom", None, 0.72),
        "stratford-upon-avon hotel area": ("Stratford-upon-Avon hotel area", "hotel", 52.1917, -1.7083, "Stratford-upon-Avon", "United Kingdom", None, 0.72),
        "cotswolds hotel area": ("Cotswolds hotel area", "hotel", 51.8330, -1.8433, "Cotswolds", "United Kingdom", None, 0.72),
        "oxford hotel area": ("Oxford hotel area", "hotel", 51.7520, -1.2577, "Oxford", "United Kingdom", None, 0.72),
        "windsor hotel area": ("Windsor hotel area", "hotel", 51.4816, -0.6136, "Windsor", "United Kingdom", None, 0.72),
        "tower of london": ("Tower of London", "activity", 51.5081, -0.0759, "London", "United Kingdom", None, 0.95),
        "westminster abbey": ("Westminster Abbey", "activity", 51.4993, -0.1273, "London", "United Kingdom", None, 0.94),
        "westminster": ("Westminster", "activity", 51.4975, -0.1357, "London", "United Kingdom", None, 0.82),
        "windsor castle": ("Windsor Castle", "activity", 51.4839, -0.6044, "Windsor", "United Kingdom", None, 0.95),
        "edinburgh castle": ("Edinburgh Castle", "activity", 55.9486, -3.1999, "Edinburgh", "United Kingdom", None, 0.95),
        "royal mile": ("Royal Mile", "activity", 55.9500, -3.1880, "Edinburgh", "United Kingdom", None, 0.9),
        "cambridge university": ("University of Cambridge", "activity", 52.2043, 0.1149, "Cambridge", "United Kingdom", None, 0.9),
        "york minster": ("York Minster", "activity", 53.9623, -1.0819, "York", "United Kingdom", None, 0.93),
        "giant’s causeway": ("Giant's Causeway", "activity", 55.2408, -6.5116, "Bushmills", "United Kingdom", None, 0.93),
        "giant's causeway": ("Giant's Causeway", "activity", 55.2408, -6.5116, "Bushmills", "United Kingdom", None, 0.93),
        "trinity college": ("Trinity College Dublin", "activity", 53.3438, -6.2546, "Dublin", "Ireland", None, 0.91),
        "stratford-upon-avon": ("Stratford-upon-Avon", "activity", 52.1917, -1.7083, "Stratford-upon-Avon", "United Kingdom", None, 0.88),
        "cotswolds": ("Cotswolds", "activity", 51.8330, -1.8433, "Cotswolds", "United Kingdom", None, 0.84),
        "seven sisters cliffs": ("Seven Sisters Cliffs", "activity", 50.7600, 0.1475, "East Sussex", "United Kingdom", None, 0.9),
        "british museum": ("British Museum", "activity", 51.5194, -0.1270, "London", "United Kingdom", None, 0.92),
        "loch ness": ("Loch Ness", "activity", 57.3229, -4.4244, "Highlands", "United Kingdom", None, 0.9),
        "glenfinnan viaduct": ("Glenfinnan Viaduct", "activity", 56.8763, -5.4316, "Glenfinnan", "United Kingdom", None, 0.9),
        "fort william": ("Fort William", "activity", 56.8198, -5.1052, "Fort William", "United Kingdom", None, 0.9),
        "belfast city hall": ("Belfast City Hall", "activity", 54.5966, -5.9301, "Belfast", "United Kingdom", None, 0.9),
        "st. anne’s cathedral": ("St Anne's Cathedral Belfast", "activity", 54.6031, -5.9280, "Belfast", "United Kingdom", None, 0.87),
        "albert clock": ("Albert Memorial Clock", "activity", 54.6003, -5.9230, "Belfast", "United Kingdom", None, 0.88),
        "peace wall": ("Belfast Peace Wall", "activity", 54.6022, -5.9560, "Belfast", "United Kingdom", None, 0.86),
        "big fish": ("The Big Fish", "activity", 54.6015, -5.9206, "Belfast", "United Kingdom", None, 0.86),
        "大英博物馆": ("British Museum", "activity", 51.5194, -0.1270, "London", "United Kingdom", None, 0.87),
        "伦敦塔": ("Tower of London", "activity", 51.5081, -0.0759, "London", "United Kingdom", None, 0.87),
        "温莎城堡": ("Windsor Castle", "activity", 51.4839, -0.6044, "Windsor", "United Kingdom", None, 0.87),
    }

    _london_airport_alternatives = [
        {"canonical_name": "London Heathrow Airport", "iata_code": "LHR", "latitude": 51.4700, "longitude": -0.4543, "confidence": 0.65},
        {"canonical_name": "London Gatwick Airport", "iata_code": "LGW", "latitude": 51.1537, "longitude": -0.1821, "confidence": 0.6},
        {"canonical_name": "London Stansted Airport", "iata_code": "STN", "latitude": 51.8860, "longitude": 0.2389, "confidence": 0.56},
    ]

    async def resolve(self, request: PlaceResolutionRequest) -> PlaceResolutionResponse:
        resolved: list[ResolvedPlace] = []
        unresolved: list[PlaceRequest] = []
        warnings: list[str] = []

        for place in request.places:
            key = place.raw_text.strip().lower()
            if key == "london airport":
                warnings.append(
                    "Multiple possible matches found for 'London airport': Heathrow, Gatwick, Stansted, Luton, London City."
                )
                resolved.append(
                    ResolvedPlace(
                        raw_text=place.raw_text,
                        canonical_name="London airport (ambiguous)",
                        place_type="airport",
                        latitude=51.4700,
                        longitude=-0.4543,
                        country=place.country_hint or "United Kingdom",
                        city="London",
                        provider="mock",
                        confidence=0.45,
                        alternatives=self._london_airport_alternatives,
                    )
                )
                continue

            match = self._places.get(key)
            if not match:
                unresolved.append(place)
                warnings.append(f"Could not resolve place '{place.raw_text}' with mock geocoder.")
                continue

            canonical, place_type, lat, lon, city, country, iata, confidence = match
            resolved.append(
                ResolvedPlace(
                    raw_text=place.raw_text,
                    canonical_name=canonical,
                    place_type=place.place_type or place_type,
                    latitude=lat,
                    longitude=lon,
                    country=country,
                    city=city,
                    iata_code=iata,
                    external_place_id=f"mock:{key}",
                    provider="mock",
                    confidence=confidence,
                )
            )

        return PlaceResolutionResponse(
            resolved_places=resolved,
            unresolved_places=unresolved,
            warnings=warnings,
        )
