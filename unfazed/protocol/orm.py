import typing as t


@t.runtime_checkable
class DataBaseDriver(t.Protocol):
    async def setup(self) -> None: ...

    @property
    def config(self) -> t.Dict: ...

    async def migrate(self) -> None: ...


@t.runtime_checkable
class Model(t.Protocol):
    async def save(self, *args: t.Any, **kw: t.Any) -> t.Self: ...
    async def create(self, *args: t.Any, **kw: t.Any) -> t.Self: ...


@t.runtime_checkable
class QuerySet(t.Protocol):
    pass
