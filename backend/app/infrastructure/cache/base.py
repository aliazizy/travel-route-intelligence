from abc import ABC, abstractmethod
from typing import Any


class CacheProvider(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Return cached value or None when missing/expired."""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Store a value for a limited time."""
