import typing as t

from unfazed.cache import caches
from unfazed.protocol import BaseLifeSpan


class CacheClear(BaseLifeSpan):
    def __init__(self, unfazed) -> None:
        self.unfazed = unfazed

    async def on_startup(self) -> None:
        pass

    async def on_shutdown(self):
        await caches.close()

    @property
    def state(self) -> t.Dict:
        return {}
