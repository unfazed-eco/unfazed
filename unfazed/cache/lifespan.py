from unfazed.cache import caches
from unfazed.lifespan import BaseLifeSpan


class CacheClear(BaseLifeSpan):
    """
    CacheClear Lifespan class for unfazed.

    This class is used to clear all caches when the application is shutting down.

    """

    async def on_shutdown(self) -> None:
        await caches.close()
