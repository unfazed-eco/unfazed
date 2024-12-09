from unfazed.cache import caches
from unfazed.lifespan import BaseLifeSpan


class CacheClear(BaseLifeSpan):
    async def on_shutdown(self) -> None:
        await caches.close()
