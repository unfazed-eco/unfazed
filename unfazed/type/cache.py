import typing as t


class CacheOptions(t.TypedDict):
    TIMEOUT: int | None
    PREFIX: str | None
    VERSION: int | None
    MAX_ENTRIES: int
