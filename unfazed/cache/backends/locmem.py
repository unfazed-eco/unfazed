import pickle
import time
import typing as t
from asyncio import Lock
from collections import OrderedDict

from unfazed.schema import LocOptions

# Global in-memory store of cache data. Keyed by name, to provide
# multiple named local memory caches.
_caches: t.Dict[str, t.OrderedDict[str, t.Any]] = {}
_expire_info: t.Dict[str, t.Dict[str, float | None]] = {}
_locks: t.Dict[str, Lock] = {}


class LocMemCache:
    """
    Local memory cache backend implementation for single-process applications.

    This class provides an in-memory caching solution with the following features:
    - Thread-safe operations using asyncio locks
    - Configurable cache size limits
    - Automatic cache eviction when size limit is reached
    - Support for key versioning
    - Configurable key prefixing
    - TTL (Time To Live) support for cache entries

    Parameters:
        location (str): Unique identifier for this cache instance
        options (Dict[str, Any] | None): Configuration options including:
            - PREFIX: Optional prefix for cache keys
            - VERSION: Default version number for keys
            - MAX_ENTRIES: Maximum number of entries to store in cache

    Usage:
        ```python
        from unfazed.cache import caches

        # Get the default cache instance
        cache: LocMemCache = caches["default"]

        # Basic operations
        await cache.set("user:1", {"name": "John", "age": 30}, timeout=3600)
        user = await cache.get("user:1")

        # Counter operations
        await cache.set("counter", 0)
        await cache.incr("counter")  # Increment by 1
        await cache.decr("counter")  # Decrement by 1

        # Check existence
        exists = await cache.has_key("user:1")

        # Delete key
        await cache.delete("user:1")

        # Clear all entries
        await cache.clear()
        ```

    Notes:
        - This cache is not suitable for multi-process applications
        - Cache entries are stored in memory and will be lost on process restart
        - Keys are automatically evicted when the cache reaches its size limit
        - Expired entries are automatically removed on access
    """

    pickle_protocol = pickle.HIGHEST_PROTOCOL

    def __init__(
        self, location: str, options: t.Dict[str, t.Any] | None = None
    ) -> None:
        if options is None:
            options = {}
        options_model = LocOptions(**options)
        self.prefix = options_model.PREFIX or location
        self.version = options_model.VERSION
        self.max_entries = options_model.MAX_ENTRIES

        self._cache = _caches.setdefault(location, OrderedDict())
        self._expire_info = _expire_info.setdefault(location, {})
        self._lock = _locks.setdefault(location, Lock())

        self.closed = False

    def make_key(self, key: str, version: int | None = None) -> str:
        version = version or self.version
        return f"{self.prefix}:{key}:{version}"

    def get_timeout(self, timeout: float | None) -> float | None:
        if timeout is None:
            return None
        return time.time() + timeout

    async def get(
        self,
        key: str,
        default: t.Any | None = None,
        version: int | None = None,
    ) -> t.Any:
        if not await self.has_key(key):
            return default
        key = self.make_key(key, version=version)
        async with self._lock:
            pickled = self._cache[key]
            self._cache.move_to_end(key, last=False)
        return pickle.loads(pickled)

    async def set(
        self,
        key: str,
        value: t.Any,
        timeout: float | None = None,
        version: int | None = None,
    ) -> None:
        key = self.make_key(key, version=version)
        pickled = pickle.dumps(value, self.pickle_protocol)
        async with self._lock:
            if len(self._cache) >= self.max_entries:
                self._cull()

            self._cache[key] = pickled
            self._cache.move_to_end(key, last=False)
            self._expire_info[key] = self.get_timeout(timeout)

    async def incr(self, key: str, delta: int = 1, version: int | None = None) -> int:
        if not await self.has_key(key):
            raise ValueError(f"Key {key} not found")
        key = self.make_key(key, version=version)

        async with self._lock:
            pickled = self._cache[key]
            value = pickle.loads(pickled)
            new_value = value + delta
            pickled = pickle.dumps(new_value, self.pickle_protocol)
            self._cache[key] = pickled
            self._cache.move_to_end(key, last=False)
        return new_value

    async def decr(self, key: str, delta: int = -1, version: int | None = None) -> int:
        return await self.incr(key, delta, version=version)

    async def has_key(self, key: str, version: int | None = None) -> bool:
        key = self.make_key(key, version=version)
        async with self._lock:
            if key not in self._cache:
                return False
            if self._has_expired(key):
                self._delete(key)
                return False

            return True

    def _has_expired(self, key: str) -> bool:
        exp = self._expire_info.get(key, None)

        if exp is None:
            return False
        else:
            return exp <= time.time()

    def _cull(self) -> None:
        count = max(len(self._cache) - self.max_entries, 1)
        for _ in range(count):
            key, _ = self._cache.popitem()
            del self._expire_info[key]

    def _delete(self, key: str) -> bool:
        try:
            del self._cache[key]
            del self._expire_info[key]
        except KeyError:
            return False
        return True

    async def delete(self, key: str, version: int | None = None) -> bool:
        key = self.make_key(key, version=version)
        async with self._lock:
            return self._delete(key)

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()
            self._expire_info.clear()

    async def close(self) -> None:
        if self.closed:
            return
        async with self._lock:
            self._cache.clear()
            self._expire_info.clear()
            if self.prefix in _caches:
                del _caches[self.prefix]
            if self.prefix in _expire_info:
                del _expire_info[self.prefix]
            if self.prefix in _locks:
                del _locks[self.prefix]
        self.closed = True
