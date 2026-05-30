from typing import Any, Literal

from pydantic import BaseModel, Field


class ValidationWarning(BaseModel):
    code: str
    message: str
    severity: Literal["info", "warning", "error"] = "warning"
    field: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
