import typing as t

from unfazed.protocol import BaseLifeSpan as BaseLifeSpanProtocol

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class BaseLifeSpan(BaseLifeSpanProtocol):
    def __init__(self, unfazed: "Unfazed") -> None:
        self.unfazed = unfazed

    async def startup(self) -> None:
        pass  # pragma: no cover

    async def shutdown(self) -> None:
        pass  # pragma: no cover

    @property
    def state(self) -> t.Dict[str, t.Any]:
        return {}
