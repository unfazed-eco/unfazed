from unfazed.cache import caches
from unfazed.lifespan import BaseLifeSpan


class CacheClear(BaseLifeSpan):
    def __init__(self, unfazed) -> None:
        self.unfazed = unfazed

    async def on_shutdown(self):
        await caches.close()
