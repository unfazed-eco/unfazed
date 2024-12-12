import typing as t

if t.TYPE_CHECKING:
    from unfazed.cache.backends.locmem import LocMemCache  # pragma: no cover
    from unfazed.cache.backends.redis.defaultclient import (
        DefaultBackend,  # pragma: no cover
    )
    from unfazed.cache.backends.redis.serializedclient import (
        SerializerBackend,  # pragma: no cover
    )


class CacheOptions(t.TypedDict):
    TIMEOUT: int | None
    PREFIX: str | None
    VERSION: int | None
    MAX_ENTRIES: int


CacheBackend = t.TypeVar(
    "CacheBackend", bound=t.Union["LocMemCache", "DefaultBackend", "SerializerBackend"]
)
