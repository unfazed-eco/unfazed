import typing as t

from click import Parameter


class Command(t.Protocol):
    def add_arguments(self) -> t.List[Parameter | None]: ...
    async def handle(self, **option: t.Optional[t.Any]) -> None: ...
