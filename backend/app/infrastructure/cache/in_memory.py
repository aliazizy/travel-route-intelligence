import time
from typing import Any

from app.infrastructure.cache.base import CacheProvider


class InMemoryTTLCache(CacheProvider):
    def __init__(self) -> None:
        self._items: dict[str, tuple[float, Any]] = {}

    async def get(self, key: str) -> Any | None:
        item = self._items.get(key)
        if item is None:
            return None

        expires_at, value = item
        if expires_at <= time.monotonic():
            self._items.pop(key, None)
            return None

        return value

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._items[key] = (time.monotonic() + ttl_seconds, value)
