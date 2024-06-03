import typing as t

from click import Parameter


class BaseCommandMethod[T](t.Protocol):
    def add_arguments(self) -> t.Sequence[Parameter]: ...
    async def handle(self, **option: t.Optional[t.Any]) -> t.Optional[T]: ...
