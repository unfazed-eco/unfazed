import typing as t

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


@t.runtime_checkable
class BaseLifeSpan(t.Protocol):
    def __init__(self, unfazed: "Unfazed") -> None: ...

    async def on_startup(self): ...
    async def on_shutdown(self): ...

    @property
    def state(self) -> t.Dict[str, t.Any]: ...
