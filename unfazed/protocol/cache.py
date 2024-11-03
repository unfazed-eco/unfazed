import typing as t

from unfazed.type import Doc


@t.runtime_checkable
class CacheBackend(t.Protocol):
    async def get(self, key: str) -> t.Any: ...

    async def set(
        self, key: str, value: t.Any, timeout: float | None = None
    ) -> None: ...

    async def delete(self, key: str) -> None: ...

    async def incr(self, key: str, delta: int = 1) -> int: ...

    async def decr(self, key: str, delta: int = 1) -> int: ...

    async def has_key(self, key: str) -> bool: ...

    def make_key(self, key: str) -> str: ...

    async def close(self) -> None: ...


@t.runtime_checkable
class SerializerBase(t.Protocol):
    def dumps(self, value: t.Any) -> bytes: ...
    def loads(
        self, value: bytes
    ) -> t.Annotated[
        t.Any,
        Doc(description="return type depends on what serializer defined"),
    ]: ...


@t.runtime_checkable
class CompressorBase(t.Protocol):
    def compress(self, value: bytes) -> bytes: ...
    def decompress(self, value: bytes) -> bytes: ...
