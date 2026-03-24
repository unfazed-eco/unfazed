Unfazed Cache
=============

Unfazed ships with a pluggable caching framework that lets you store and retrieve data through a simple async API. You can configure multiple named cache backends — local memory for development, Redis for production — and switch between them with a single setting. A `@cached` decorator is also provided to cache function return values automatically.

## Quick Start

### 1. Add a cache backend to settings

```python
# settings.py
UNFAZED_SETTINGS = {
    "PROJECT_NAME": "myproject",
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "default_cache",
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
            },
        },
    },
    "LIFESPAN": [
        "unfazed.cache.lifespan.CacheClear",
    ],
}
```

### 2. Use the cache

```python
from unfazed.cache import caches

cache = caches["default"]

await cache.set("greeting", "hello", timeout=60)
value = await cache.get("greeting")  # "hello"
```

## Configuration

The `CACHE` setting is a dictionary where each key is a cache alias (e.g. `"default"`, `"sessions"`) and each value describes the backend:

```python
"CACHE": {
    "<alias>": {
        "BACKEND": "<dotted.path.to.BackendClass>",
        "LOCATION": "<backend-specific location>",
        "OPTIONS": { ... },
    },
}
```

| Field | Description |
|-------|-------------|
| `BACKEND` | Dotted import path to the cache backend class. |
| `LOCATION` | Backend-specific location. For LocMem: a unique name string. For Redis: a connection URL like `redis://localhost:6379/0`. |
| `OPTIONS` | Dict of backend-specific options (see each backend below). |

You can define as many named caches as you need and access them by alias:

```python
default = caches["default"]
sessions = caches["sessions"]
```

## Built-in Backends

### LocMemCache — Local Memory

A simple in-process cache backed by an `OrderedDict`. Good for development and single-process deployments. Data is lost when the process restarts.

**Backend path:** `unfazed.cache.backends.locmem.LocMemCache`

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `PREFIX` | `str` | location value | Key prefix for namespace isolation. |
| `VERSION` | `int` | `None` | Default version appended to keys. |
| `MAX_ENTRIES` | `int` | `300` | Maximum number of entries. Oldest entries are evicted when full. |

**Configuration example:**

```python
"CACHE": {
    "default": {
        "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
        "LOCATION": "my_cache",
        "OPTIONS": {
            "MAX_ENTRIES": 500,
            "PREFIX": "myapp",
        },
    },
}
```

### DefaultBackend — Raw Redis

A thin wrapper around `redis.asyncio.Redis` that adds key prefixing and connection management. All standard Redis commands are available through attribute proxying — you call Redis methods directly on the backend instance.

**Backend path:** `unfazed.cache.backends.redis.DefaultBackend`

**Configuration example:**

```python
"CACHE": {
    "default": {
        "BACKEND": "unfazed.cache.backends.redis.DefaultBackend",
        "LOCATION": "redis://localhost:6379/0",
        "OPTIONS": {
            "PREFIX": "myapp",
            "max_connections": 20,
            "decode_responses": True,
        },
    },
}
```

### SerializerBackend — Redis with Serialization

Extends Redis with automatic serialization and optional compression, so you can store complex Python objects (dicts, lists, dataclasses, etc.) transparently. Uses Pickle + Zlib by default.

**Backend path:** `unfazed.cache.backends.redis.SerializerBackend`

**Configuration example:**

```python
"CACHE": {
    "default": {
        "BACKEND": "unfazed.cache.backends.redis.SerializerBackend",
        "LOCATION": "redis://localhost:6379/0",
        "OPTIONS": {
            "PREFIX": "myapp",
            "SERIALIZER": "unfazed.cache.serializers.pickle.PickleSerializer",
            "COMPRESSOR": "unfazed.cache.compressors.zlib.ZlibCompressor",
        },
    },
}
```

**Redis OPTIONS reference** (applies to both `DefaultBackend` and `SerializerBackend`):

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `PREFIX` | `str` | `None` | Key prefix for namespace isolation. |
| `SERIALIZER` | `str` | `PickleSerializer` | Dotted path to serializer class (SerializerBackend only). |
| `COMPRESSOR` | `str` | `ZlibCompressor` | Dotted path to compressor class (SerializerBackend only). Requires a serializer. |
| `max_connections` | `int` | `10` | Maximum connections in the pool. |
| `decode_responses` | `bool` | `False` | Decode Redis bytes to strings. Not supported by SerializerBackend. |
| `socket_timeout` | `int` | `None` | Socket timeout in seconds. |
| `socket_connect_timeout` | `int` | `None` | Connection timeout in seconds. |
| `health_check_interval` | `int` | `30` | Seconds between health checks. |
| `retry_on_timeout` | `bool` | `False` | Retry on timeout errors. |
| `ssl` | `bool` | `False` | Enable SSL/TLS. |

## Examples

### LocMem: Basic Operations

```python
from unfazed.cache import caches

cache = caches["default"]

# Set a value with a 5-minute TTL
await cache.set("user:1:name", "Alice", timeout=300)

# Get a value (returns None if missing or expired)
name = await cache.get("user:1:name")

# Get with a fallback default
name = await cache.get("user:1:name", default="Anonymous")

# Check existence
if await cache.has_key("user:1:name"):
    print("Key exists")

# Delete a key
await cache.delete("user:1:name")

# Counters
await cache.set("hits", 0)
await cache.incr("hits")      # 1
await cache.incr("hits")      # 2
await cache.decr("hits")      # 1

# Clear everything
await cache.clear()
```

### Redis DefaultBackend: Full Redis API

Because `DefaultBackend` proxies all attribute access to the underlying `redis.asyncio.Redis` client, you can use any Redis command directly. Just remember to call `make_key()` for prefix support:

```python
from unfazed.cache import caches

cache = caches["default"]  # a DefaultBackend instance

# String operations
await cache.set(cache.make_key("token"), "abc123", ex=3600)
token = await cache.get(cache.make_key("token"))

# Hash operations
await cache.hset(cache.make_key("user:1"), mapping={"name": "Alice", "role": "admin"})
user = await cache.hgetall(cache.make_key("user:1"))

# List operations
await cache.rpush(cache.make_key("queue"), "task1", "task2")
task = await cache.lpop(cache.make_key("queue"))

# Set operations
await cache.sadd(cache.make_key("tags"), "python", "async")
tags = await cache.smembers(cache.make_key("tags"))
```

### Redis SerializerBackend: Storing Python Objects

`SerializerBackend` wraps string commands with automatic serialization, so you can store and retrieve Python objects directly:

```python
from unfazed.cache import caches

cache = caches["default"]  # a SerializerBackend instance

# Store a dict — automatically serialized + compressed
await cache.set("user:1", {"name": "Alice", "roles": ["admin", "editor"]}, ex=3600)

# Retrieve it — automatically decompressed + deserialized
user = await cache.get("user:1")  # {"name": "Alice", "roles": ["admin", "editor"]}

# Integer/float values pass through without serialization
await cache.set("counter", 0)
await cache.incr("counter")   # 1
await cache.decr("counter")   # 0

# Bulk operations
await cache.mset({"key1": {"a": 1}, "key2": [1, 2, 3]})
values = await cache.mget(["key1", "key2"])

# Check TTL and existence
await cache.set("temp", "data", ex=60)
ttl = await cache.ttl("temp")       # seconds remaining
exists = await cache.exists("temp")  # 1 if exists
```

### Multi-Backend Setup

A typical production configuration uses LocMem for ephemeral data and Redis for shared state:

```python
# settings.py
UNFAZED_SETTINGS = {
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.redis.SerializerBackend",
            "LOCATION": "redis://redis-host:6379/0",
            "OPTIONS": {
                "PREFIX": "myapp",
                "max_connections": 20,
            },
        },
        "local": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "local_cache",
            "OPTIONS": {"MAX_ENTRIES": 500},
        },
    },
    "LIFESPAN": ["unfazed.cache.lifespan.CacheClear"],
}
```

```python
from unfazed.cache import caches

redis_cache = caches["default"]
local_cache = caches["local"]
```

## The `@cached` Decorator

The `@cached` decorator caches function return values automatically. It works with both async and sync functions.

```python
from unfazed.cache import cached


@cached(timeout=300)
async def get_user_profile(user_id: int) -> dict:
    # expensive database query
    ...
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `using` | `str` | `"default"` | Cache alias to use. |
| `timeout` | `int` | `60` | TTL in seconds. |
| `include` | `List[str]` | `None` | Parameter names to include in the cache key. If `None`, all keyword arguments are used. |

**Cache key format:** `module_name:function_name:param1_value:param2_value`

**Selecting key parameters** — use `include` when some arguments shouldn't affect the cache key:

```python
@cached(timeout=120, include=["user_id"])
async def get_dashboard(user_id: int, request_time: str) -> dict:
    # Only user_id is part of the cache key; request_time is ignored
    ...
```

**Using a specific backend:**

```python
@cached(using="local", timeout=60)
async def get_config(key: str) -> str:
    ...
```

**Forcing a cache refresh** — pass `force_update=True` to bypass the cache and store a fresh result.  
Recommended: declare `force_update: bool = False` in the decorated function for explicit API and better readability:

```python
@cached(timeout=60)
async def get_user_profile(user_id: int, force_update: bool = False) -> dict:
    ...

result = await get_user_profile(user_id=42, force_update=True)
```

If the decorated function defines neither `force_update` nor `**kwargs`, `@cached` emits a warning at decoration/import time.  
Calling that function with `force_update=...` may still raise a `TypeError` from Python function-call semantics.

**Important:**
- The decorator only uses keyword arguments for the cache key. Positional arguments are ignored (a warning is emitted if you pass them).
- `@cached` validates the function signature at decoration time and emits warnings for unsupported/ambiguous `force_update` usage (for example missing `force_update`/`**kwargs`, or non-`bool` annotation).
- `@cached` does not enforce a runtime boolean type check for `force_update`; runtime behavior follows Python truthiness.

## Custom Serializers & Compressors

You can replace the default Pickle/Zlib implementations by writing classes that follow the `SerializerBase` or `CompressorBase` protocols.

**Custom serializer:**

```python
# myapp/cache_serializer.py
import json


class JsonSerializer:
    def dumps(self, value: any) -> bytes:
        return json.dumps(value).encode("utf-8")

    def loads(self, value: bytes) -> any:
        return json.loads(value.decode("utf-8"))
```

**Custom compressor:**

```python
# myapp/cache_compressor.py
import lzma


class LzmaCompressor:
    def compress(self, value: bytes) -> bytes:
        return lzma.compress(value)

    def decompress(self, value: bytes) -> bytes:
        return lzma.decompress(value)
```

**Register them in settings:**

```python
"CACHE": {
    "default": {
        "BACKEND": "unfazed.cache.backends.redis.SerializerBackend",
        "LOCATION": "redis://localhost:6379/0",
        "OPTIONS": {
            "SERIALIZER": "myapp.cache_serializer.JsonSerializer",
            "COMPRESSOR": "myapp.cache_compressor.LzmaCompressor",
        },
    },
}
```

## Shutdown Cleanup

Add the built-in `CacheClear` lifespan to your settings to ensure all cache connections are properly closed when the server shuts down:

```python
"LIFESPAN": [
    "unfazed.cache.lifespan.CacheClear",
]
```

This calls `await caches.close()` during the shutdown phase, which closes every registered backend.

## API Reference

### CacheHandler (singleton: `caches`)

```python
class CacheHandler(Storage[CacheBackend])
```

Global registry of cache backends. Access it via the `caches` singleton.

- `caches["alias"]` — get a backend by alias (`KeyError` if missing).
- `caches["alias"] = backend` — register a backend.
- `del caches["alias"]` — remove a backend.
- `"alias" in caches` — check existence.
- `async close() -> None`: Close all registered backends.

### LocMemCache

```python
class LocMemCache(location: str, options: Dict[str, Any] | None = None)
```

In-process cache with automatic eviction.

- `async get(key: str, default: Any = None, version: int | None = None) -> Any`
- `async set(key: str, value: Any, timeout: float | None = None, version: int | None = None) -> None`
- `async delete(key: str, version: int | None = None) -> bool`
- `async has_key(key: str, version: int | None = None) -> bool`
- `async incr(key: str, delta: int = 1, version: int | None = None) -> int`
- `async decr(key: str, delta: int = -1, version: int | None = None) -> int`
- `async clear() -> None`
- `async close() -> None`
- `make_key(key: str, version: int | None = None) -> str`

### DefaultBackend

```python
class DefaultBackend(location: str, options: Dict[str, Any] | None = None)
```

Raw Redis backend. Proxies all Redis commands through `__getattr__`, so any `redis.asyncio.Redis` method is available directly.

- `make_key(key: str) -> str`: Prepend the configured prefix.
- `async close() -> None`: Close the Redis connection.
- Supports `async with` context manager.

### SerializerBackend

```python
class SerializerBackend(location: str, options: Dict[str, Any] | None = None)
```

Redis backend with transparent serialization and compression.

**String commands** (serialized): `get`, `set`, `getdel`, `getex`, `getset`, `mget`, `mset`, `msetnx`, `setex`, `setnx`, `psetex`.

**Numeric commands** (pass-through): `incr`, `incrby`, `incrbyfloat`, `decr`, `decrby`.

**General commands**: `exists`, `expire`, `touch`, `ttl`, `delete`, `flushdb`.

- `make_key(key: str) -> str`: Prepend the configured prefix.
- `encode(value: Any) -> int | float | bytes`: Serialize and optionally compress a value.
- `decode(value: bytes | None) -> Any`: Decompress and deserialize a value.
- `async close() -> None`: Close the Redis connection.
- Supports `async with` context manager.

### cached

```python
def cached(using: str = "default", timeout: int = 60, include: List[str] | None = None) -> Callable
```

Decorator that caches function return values. Works with both async and sync functions.

### CacheClear

```python
class CacheClear(BaseLifeSpan)
```

Lifespan hook that calls `await caches.close()` on shutdown.

- `async on_shutdown() -> None`: Closes all cache backends.
