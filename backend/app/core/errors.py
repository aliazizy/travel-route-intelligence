from enum import StrEnum
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorCode(StrEnum):
    validation_error = "VALIDATION_ERROR"
    llm_extraction_failed = "LLM_EXTRACTION_FAILED"
    geocoding_failed = "GEOCODING_FAILED"
    routing_failed = "ROUTING_FAILED"
    internal_error = "INTERNAL_ERROR"


class ErrorBody(BaseModel):
    code: ErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    recoverable: bool = True


class ErrorResponse(BaseModel):
    error: ErrorBody


class AppError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        recoverable: bool = True,
        status_code: int = 400,
    ) -> None:
        self.body = ErrorBody(
            code=code,
            message=message,
            details=details or {},
            recoverable=recoverable,
        )
        self.status_code = status_code


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.body).model_dump(mode="json"),
    )
