import json
from types import SimpleNamespace

import pytest

from app.domain.models.itinerary import TravelRequest
from app.infrastructure.llm.azure_openai_provider import AzureOpenAIProvider
from app.infrastructure.llm.base import LLMProviderError


class FakeChatCompletions:
    def __init__(self, content: str) -> None:
        self.content = content
        self.last_kwargs = {}

    async def create(self, **kwargs):
        self.last_kwargs = kwargs
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))]
        )


@pytest.mark.asyncio
async def test_azure_provider_validates_structured_response() -> None:
    payload = {
        "parsed_itinerary": {
            "arrival": {
                "name": "Heathrow",
                "place_type": "airport",
                "city_hint": "London",
                "country_hint": "United Kingdom",
                "role": "arrival",
                "day": 1,
                "nights": None,
                "locked": True,
                "confidence": 0.93,
                "inferred": False,
            },
            "departure": None,
            "cities": [],
            "hotels": [],
            "activities": [],
            "restaurants": [],
            "transport": {"mode": "coach"},
            "constraints": [],
        },
        "raw_entities": [
            {
                "text": "Heathrow",
                "entity_type": "AIRPORT",
                "start_char": None,
                "end_char": None,
                "confidence": 0.93,
                "source": "llm",
            }
        ],
        "warnings": [],
        "confidence_score": 0.9,
    }
    fake_client = FakeChatCompletions(json.dumps(payload))
    provider = AzureOpenAIProvider(
        endpoint="https://example.openai.azure.com",
        api_key="test",
        deployment="model-router",
        api_version="2025-01-01-preview",
        chat_completions=fake_client,
    )

    result = await provider.parse_itinerary(TravelRequest(request_text="Arrive Heathrow"))

    assert result.parsed_itinerary.arrival is not None
    assert result.parsed_itinerary.arrival.name == "Heathrow"
    assert fake_client.last_kwargs["model"] == "model-router"
    assert fake_client.last_kwargs["response_format"]["type"] == "json_schema"


@pytest.mark.asyncio
async def test_azure_provider_rejects_invalid_response_json() -> None:
    provider = AzureOpenAIProvider(
        endpoint="https://example.openai.azure.com",
        api_key="test",
        deployment="model-router",
        api_version="2025-01-01-preview",
        chat_completions=FakeChatCompletions("{}"),
    )

    with pytest.raises(LLMProviderError):
        await provider.parse_itinerary(TravelRequest(request_text="Arrive Heathrow"))
