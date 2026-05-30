from app.core.config import Settings
from app.core.errors import AppError, ErrorCode
from app.infrastructure.llm.azure_openai_provider import AzureOpenAIProvider
from app.infrastructure.llm.base import LLMProvider
from app.infrastructure.llm.mock_provider import MockLLMProvider


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "mock":
        return MockLLMProvider()

    if settings.llm_provider == "azure_openai":
        missing = [
            name
            for name, value in {
                "AZURE_OPENAI_ENDPOINT": settings.azure_openai_endpoint,
                "AZURE_OPENAI_API_KEY": settings.azure_openai_api_key,
                "AZURE_OPENAI_DEPLOYMENT": settings.azure_openai_deployment,
            }.items()
            if not value
        ]
        if missing:
            raise AppError(
                ErrorCode.llm_extraction_failed,
                "Azure OpenAI provider is selected but required settings are missing.",
                details={"missing": missing},
                status_code=500,
            )
        return AzureOpenAIProvider(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            deployment=settings.azure_openai_deployment,
            api_version=settings.azure_openai_api_version,
        )

    raise AppError(
        ErrorCode.llm_extraction_failed,
        f"LLM provider '{settings.llm_provider}' is not implemented yet.",
        recoverable=True,
        status_code=501,
    )
