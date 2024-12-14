from unfazed.type import CacheBackend
from unfazed.utils import Storage


class CacheHandler(Storage[CacheBackend]):
    """
    Cache Handler class for unfazed.


    Usage:

    ```python

    from unfazed.cache import caches


    default = caches["default"]

    await default.set("key", "value")
    ret = await default.get("key")

    ```

    """

    async def close(self) -> None:
        for backend in self.storage.values():
            await backend.close()


caches: CacheHandler = CacheHandler()
