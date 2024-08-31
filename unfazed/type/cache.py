import typing as t


class CacheOptions(t.TypedDict):
    TIMEOUT: int | None = None
    PREFIX: str | None = None
    VERSION: int | None = None
    MAX_ENTRIES: int = 300
