from unfazed.protocol import CacheBackend
from unfazed.utils import Storage


class CacheHandler(Storage[CacheBackend]):
    async def close(self):
        for backend in self.storage.values():
            await backend.close()


caches = CacheHandler()
