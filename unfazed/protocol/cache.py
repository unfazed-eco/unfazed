import typing as t

from unfazed.type import Doc


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
