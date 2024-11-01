from asgiref.local import Local

from unfazed.protocol import CacheBackend


class CacheHandler:
    def __init__(self) -> None:
        self.storage = Local()

    def __getitem__(self, key: str) -> CacheBackend:
        try:
            return getattr(self.storage, key)
        except AttributeError:
            raise KeyError(f"Unfazed Error: CacheBackend {key} not found")

    def __setitem__(self, key: str, backend: CacheBackend) -> None:
        setattr(self.storage, key, backend)

    def __contains__(self, key: str) -> bool:
        return hasattr(self.storage, key)


caches = CacheHandler()
