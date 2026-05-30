import json
from typing import Any, Protocol

import structlog
from openai import AsyncAzureOpenAI, OpenAIError
from pydantic import ValidationError

from app.domain.models.itinerary import ParseItineraryResponse, TravelRequest
from app.infrastructure.llm.base import LLMProviderError
from app.infrastructure.llm.extraction_prompt import EXTRACTION_RESPONSE_SCHEMA, EXTRACTION_SYSTEM_PROMPT

logger = structlog.get_logger(__name__)


class ChatCompletionsClient(Protocol):
    async def create(self, **kwargs: Any) -> Any:
        """Subset of the OpenAI chat completions API used by this provider."""


class AzureOpenAIProvider:
    def __init__(
        self,
        *,
        endpoint: str,
        api_key: str,
        deployment: str,
        api_version: str,
        chat_completions: ChatCompletionsClient | None = None,
    ) -> None:
        self.deployment = deployment
        self._chat_completions = chat_completions or AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        ).chat.completions

    async def parse_itinerary(self, request: TravelRequest) -> ParseItineraryResponse:
        user_payload = {
            "request_text": request.request_text,
            "default_country": request.default_country,
            "language": request.language,
            "client_context": request.client_context,
        }
        try:
            completion = await self._chat_completions.create(
                model=self.deployment,
                temperature=0,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "travel_itinerary_extraction",
                        "strict": True,
                        "schema": EXTRACTION_RESPONSE_SCHEMA,
                    },
                },
                messages=[
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
                ],
            )
        except OpenAIError as exc:
            logger.warning("azure_openai_extraction_failed", error_type=type(exc).__name__)
            raise LLMProviderError("Azure OpenAI extraction failed.") from exc

        content = self._extract_content(completion)
        try:
            return ParseItineraryResponse.model_validate_json(content)
        except ValidationError as exc:
            logger.warning("azure_openai_invalid_extraction_json", error_count=len(exc.errors()))
            raise LLMProviderError("Azure OpenAI returned invalid itinerary JSON.") from exc

    def _extract_content(self, completion: Any) -> str:
        try:
            content = completion.choices[0].message.content
        except (AttributeError, IndexError) as exc:
            raise LLMProviderError("Azure OpenAI response did not include message content.") from exc

        if isinstance(content, str) and content.strip():
            return content

        raise LLMProviderError("Azure OpenAI response content was empty.")
