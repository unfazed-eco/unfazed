from unfazed.type import CacheBackend
from unfazed.utils import Storage


class CacheHandler(Storage[CacheBackend]):
    """
    A handler class for managing multiple cache backends in unfazed.

    This class provides a unified interface for interacting with different cache backends.
    It inherits from Storage[CacheBackend] and manages the lifecycle of cache instances.

    Attributes:
        storage (Dict[str, CacheBackend]): A dictionary mapping backend names to their instances.

    Examples:
        Basic usage:
        ```python
        from unfazed.cache import caches

        # Get default cache backend
        default = caches["default"]

        # Set and get values
        await default.set("key", "value")
        value = await default.get("key")
        ```

        Using different backends:
        ```python
        # Get specific cache backend
        redis = caches["redis"]

        # Set value with timeout
        await redis.set("key", "value", timeout=60)

        # Get value with default
        value = await redis.get("key", default="default_value")
        ```

        Error handling:
        ```python
        try:
            cache = caches["non_existent"]
        except KeyError:
            print("Cache backend not found")
        ```

    Notes:
        - The cache handler is a singleton instance accessible via `caches`.
        - Each cache backend must be configured before use.
        - Cache operations are asynchronous and must be awaited.
        - The handler automatically manages the lifecycle of cache backends.
    """

    async def close(self) -> None:
        """
        Close all cache backends and release resources.

        This method should be called when the application is shutting down
        to ensure proper cleanup of cache connections.

        Examples:
            ```python
            await caches.close()
            ```

        Notes:
            - This method should be called during application shutdown.
            - It will close all configured cache backends.
            - After calling this method, the cache backends should not be used.
        """
        for backend in self.storage.values():
            await backend.close()


caches: CacheHandler = CacheHandler()
