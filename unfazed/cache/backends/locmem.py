import pickle
import time
import typing as t
from asyncio import Lock
from collections import OrderedDict

from unfazed.protocol import CacheBackend
from unfazed.schema import LocOptions

# Global in-memory store of cache data. Keyed by name, to provide
# multiple named local memory caches.
_caches = {}
_expire_info = {}
_locks = {}


class LocMemCache(CacheBackend):
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

    def get_timeout(self, timeout: float | None) -> int:
        if timeout is None:
            return None
        return time.time() + timeout

    async def get(self, key: str, default=None, version=None) -> t.Any:
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
        version=None,
    ) -> None:
        key = self.make_key(key, version=version)
        pickled = pickle.dumps(value, self.pickle_protocol)
        async with self._lock:
            if len(self._cache) >= self.max_entries:
                self._cull()

            self._cache[key] = pickled
            self._cache.move_to_end(key, last=False)
            self._expire_info[key] = self.get_timeout(timeout)

    async def incr(self, key: str, delta=1, version=None) -> int:
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

    async def decr(self, key: str, delta=-1, version=None) -> int:
        return await self.incr(key, delta, version=version)

    async def has_key(self, key, version=None) -> bool:
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

    async def delete(self, key: str, version=None) -> bool:
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
            del _caches[self.prefix]
            del _expire_info[self.prefix]
            del _locks[self.prefix]
        self.closed = True
