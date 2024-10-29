import typing as t

from unfazed.protocol import BaseLifeSpan

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class SetCount(BaseLifeSpan):
    def __init__(self, unfazed: "Unfazed"):
        self.unfazed = unfazed
        self.count = 0

    async def on_startup(self) -> None:
        self.count += 1

    async def on_shutdown(self) -> None:
        self.count += 1
