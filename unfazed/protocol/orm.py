import typing as t


@t.runtime_checkable
class DataBaseDriver(t.Protocol):
    async def setup(self) -> None: ...

    @property
    def config(self) -> t.Dict: ...


@t.runtime_checkable
class Model(t.Protocol):
    pass
