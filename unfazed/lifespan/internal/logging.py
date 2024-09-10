import typing as t

from unfazed.protocol import BaseLifeSpan

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed


class LogClean(BaseLifeSpan):
    def __init__(self, unfazed: "Unfazed") -> None:
        self.unfazed = unfazed

    async def on_startup(self) -> None:
        pass

    async def on_shutdown(self) -> None:
        logconfig = self.unfazed.settings.LOGGING

        if not logconfig:
            return

        if "handlers" not in logconfig:
            return

    @property
    def state(self) -> t.Dict:
        return {}
