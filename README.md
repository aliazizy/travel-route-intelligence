# Travel Route Intelligence MVP

AI-assisted travel itinerary geo-sequencing and map visualisation system.

This first increment is a working vertical slice:

- FastAPI backend with clean provider boundaries.
- Deterministic mock itinerary parser, mock geocoder and mock route calculator.
- Sequence builder that preserves arrival, overnight city blocks, activities and departure.
- GeoJSON generation for markers and route segments.
- React + TypeScript frontend with request input, Leaflet map, numbered markers, warnings, timeline and JSON exports.
- Backend and frontend tests.
- Docker Compose with backend, frontend, PostGIS and Redis.

## Architecture

The backend follows a clean architecture split:

- `api`: FastAPI routers and request/response wiring.
- `application`: use cases and workflow orchestration.
- `domain`: Pydantic models and deterministic business services.
- `infrastructure`: swappable providers for LLM extraction, geocoding and routing.

The frontend is split into:

- `api`: typed client calls and response types.
- `components`: map, input, timeline, warnings, route summary and JSON preview.
- `features/itinerary`: local Zustand state for selected itinerary output.
- `pages`: planner layout.

## Run Locally

Copy environment defaults:

```bash
cp .env.example .env
```

Start the full stack:

```bash
docker compose up --build
```

Open:

- Frontend: http://localhost:4000
- Backend docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Backend Development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn app.main:app --reload
```

## Frontend Development

```bash
cd frontend
npm install
npm run dev
npm test
```

## MVP Endpoint

`POST /api/v1/workflows/full-process`

Runs:

free text -> mock extraction -> mock geocoding -> sequence builder -> mock routes -> GeoJSON

The response includes parsed itinerary data, entities, resolved places, unresolved places, route segments, warnings and confidence scores.

## Provider Configuration

The backend defaults to mock providers when no `.env` is present. To enable Azure OpenAI extraction, set:

```bash
LLM_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=model-router
AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

Keep `LLM_PROVIDER=mock` for deterministic local testing and CI.

To enable Google geocoding, set:

```bash
GEOCODER_PROVIDER=google
GOOGLE_MAPS_API_KEY=...
GEOCODING_CACHE_TTL_SECONDS=86400
```

Keep `GEOCODER_PROVIDER=mock` when you want the deterministic fixture geocoder.

To enable OpenRouteService routing, set:

```bash
ROUTING_PROVIDER=openrouteservice
OPENROUTESERVICE_API_KEY=...
ROUTING_CACHE_TTL_SECONDS=86400
```

Keep `ROUTING_PROVIDER=mock` when you want straight-line deterministic routes.

## Known MVP Limitations

- The parser is deterministic and covers only representative sample patterns.
- Geocoding uses a small in-memory fixture set.
- Route geometry is a straight line between points, with haversine estimates.
- UI edit controls are presented as the next increment but not persisted yet.
- PostGIS and Redis are included in Docker Compose but not wired into repositories/caching yet.

## Next Implementation Step

Replace the mock parser with a real GPT-5.x or Azure OpenAI structured extraction provider:

1. Add a strict JSON schema for `ParsedItinerary`, extracted entities, warnings and confidence.
2. Implement `OpenAIProvider` and `AzureOpenAIProvider` behind `LLMProvider`.
3. Add provider selection via environment configuration.
4. Add tests using recorded/mock OpenAI responses.
5. Keep the mock provider as the default for local development and CI.

After that, replace the mock geocoder with Mapbox or Google geocoding plus a Nominatim fallback and Redis/database caching.
