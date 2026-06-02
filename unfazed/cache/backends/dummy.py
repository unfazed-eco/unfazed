import typing as t


async def _noop(*args: t.Any, **kwargs: t.Any) -> None:
    return None


class DummyCache:
    """
    Dummy cache backend that proxies any method call without producing actual effects.

    This is useful for development and testing when you want to disable caching
    without changing your application code. All method calls are accepted but
    produce no side effects, and return sensible no-op defaults.

    Parameters:
        location (str): Unique identifier for this cache instance
        options (Dict[str, Any] | None): Configuration options (ignored)

    Usage:
        ```python
        from unfazed.cache import caches

        cache: DummyCache = caches["default"]

        # All operations are no-ops
        await cache.set("key", "value")       # Does nothing
        value = await cache.get("key")         # Returns None
        await cache.hset("hash", "f", "v")     # Proxied, no-op
        ```
    """

    def __init__(
        self, location: str, options: t.Dict[str, t.Any] | None = None
    ) -> None:
        self.location = location
        self.closed = False

    async def get(
        self,
        key: str,
        default: t.Any | None = None,
        version: int | None = None,
    ) -> t.Any:
        return default

    async def set(
        self,
        key: str,
        value: t.Any,
        timeout: float | None = None,
        version: int | None = None,
    ) -> None:
        return None

    async def incr(self, key: str, delta: int = 1, version: int | None = None) -> int:
        return 0

    async def decr(self, key: str, delta: int = 1, version: int | None = None) -> int:
        return 0

    async def has_key(self, key: str, version: int | None = None) -> bool:
        return False

    async def delete(self, key: str, version: int | None = None) -> bool:
        return False

    async def clear(self) -> None:
        return None

    async def close(self) -> None:
        self.closed = True

    def __getattr__(self, name: str) -> t.Any:
        return _noop
