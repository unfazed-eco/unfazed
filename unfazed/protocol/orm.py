import typing as t


@t.runtime_checkable
class DataBaseDriver(t.Protocol):
    async def setup(self) -> None: ...

    @property
    def config(self) -> t.Dict: ...


@t.runtime_checkable
class Model(t.Protocol):
    async def save(self, *args, **kw): ...
    async def create(self, *args, **kw): ...


@t.runtime_checkable
class QuerySet(t.Protocol):
    pass
