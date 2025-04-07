from unfazed.cache import caches
from unfazed.lifespan import BaseLifeSpan


class CacheClear(BaseLifeSpan):
    """
    CacheClear Lifespan class for unfazed.

    This class implements the shutdown lifecycle hook to ensure proper cleanup
    of all cache resources when the application is shutting down. It is designed
    to be used as a lifespan manager in FastAPI applications.

    Attributes:
        Inherits all attributes from BaseLifeSpan.

    Methods:
        on_shutdown: Asynchronous method that handles cache cleanup during
                    application shutdown.

    """

    async def on_shutdown(self) -> None:
        """
        Handle cache cleanup during application shutdown.

        This method is called automatically when the application is shutting down.
        It ensures that all cache connections are properly closed and resources
        are cleaned up.

        Returns:
            None
        """
        await caches.close()
