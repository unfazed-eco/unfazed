from unfazed.protocol import CacheBackend


class CacheHandler:
    def __init__(self) -> None:
        self.storage = {}

    def __getitem__(self, key: str) -> CacheBackend:
        try:
            return self.storage[key]
        except KeyError:
            raise KeyError(f"Unfazed Error: CacheBackend {key} not found")

    def __setitem__(self, key: str, backend: CacheBackend) -> None:
        self.storage[key] = backend

    def __contains__(self, key: str) -> bool:
        return key in self.storage

    def __delitem__(self, key: str) -> None:
        del self.storage[key]

    async def close(self):
        for backend in self.storage.values():
            await backend.close()


caches = CacheHandler()
