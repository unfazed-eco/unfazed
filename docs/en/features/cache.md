# Unfazed Cache System

Unfazed provides a complete caching solution that supports multiple cache backends, including in-process memory cache and Redis cache. The cache system is flexibly designed and supports advanced features such as serialization, compression, key prefixes, and version control.

For more advanced redis client, see [unfazed-redis](https://github.com/unfazed-eco/unfazed-redis)


For redis client with monitoring, see [unfazed-prometheus](https://github.com/unfazed-eco/unfazed-prometheus)



## Core Features

- **Multiple Backend Support**: In-process memory cache and Redis cache
- **Async Operations**: Fully async API design, supports high concurrency
- **Serialization Support**: Automatic serialization of complex Python objects
- **Compression Support**: Optional zlib compression to reduce storage space
- **Key Management**: Support for key prefixes, version control, automatic expiration
- **Decorator Support**: `@cached` decorator simplifies cache usage

## Cache Handler

The Unfazed cache system uses the `CacheHandler` class to manage multiple cache backends, providing a unified interface.

### Core Components

- **caches**: Global cache handler instance, manages all configured cache backends
- **CacheHandler**: Inherits from `Storage[CacheBackend]`, provides cache lifecycle management


### Usage

```python
from unfazed.cache import caches

# Get default cache
default_cache = caches["default"]

# Get specific cache
redis_cache = caches["redis"]

```

## Quick Start

### 1. Basic Configuration

```python
# settings.py
UNFAZED_SETTINGS = {
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "default_cache",
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
                "PREFIX": "default",
                "VERSION": 1,
            },
        },
        "redis": {
            "BACKEND": "unfazed.cache.backends.redis.defaultclient.DefaultBackend",
            "LOCATION": "redis://localhost:6379/0",
            "OPTIONS": {
                "PREFIX": "app_cache",
                "MAX_CONNECTIONS": 10,
                "HEALTH_CHECK_INTERVAL": 30,
            },
        },
        "redis_serialized": {
            "BACKEND": "unfazed.cache.backends.redis.serializedclient.SerializerBackend",
            "LOCATION": "redis://localhost:6379/0",
            "OPTIONS": {
                "PREFIX": "serialized_cache",
                "SERIALIZER": "unfazed.cache.serializers.pickle.PickleSerializer",
                "COMPRESSOR": "unfazed.cache.compressors.zlib.ZlibCompressor",
            },
        },
    }
}
```

### 2. Basic Usage

```python
from unfazed.cache import caches

async def basic_usage():
    # Get cache instance
    cache = caches["default"]
    
    # Set cache
    await cache.set("user:1", "value", timeout=3600)
    
    # Get cache
    user = await cache.get("user:1")
    
    # Check if key exists
    exists = await cache.has_key("user:1")
    
    # Delete cache
    await cache.delete("user:1")
    
    # Clear all cache
    await cache.clear()
```

## In-Process Memory Cache

In-process memory cache (`LocMemCache`) is suitable for single-process applications, providing high-performance memory storage.

### Features

- **Thread Safe**: Uses asyncio Lock to ensure concurrency safety
- **Automatic Cleanup**: Supports TTL and maximum entry limits
- **LRU Strategy**: Uses OrderedDict to implement LRU cache eviction
- **Version Control**: Supports key version management
- **Key Prefix**: Supports key name prefix isolation

### Configuration Options

```python
UNFAZED_SETTINGS = {
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "app_cache",  # Unique identifier for cache instance
            "OPTIONS": {
                "PREFIX": "app",      # Key prefix
                "VERSION": 1,         # Default version number
                "MAX_ENTRIES": 1000,  # Maximum cache entries
            },
        },
    }
}
```

### Advanced Usage

```python
from unfazed.cache import caches
from unfazed.cache.backends.locmem import LocMemCache

async def advanced_locmem_usage():
    cache: LocMemCache = caches["default"]
    
    # Counter operations
    await cache.set("counter", 0)
    await cache.incr("counter")      # Increment by 1
    await cache.incr("counter", 5)   # Increment by 5
    await cache.decr("counter", 2)   # Decrement by 2
    
    # Version control
    await cache.set("key", "value", version=1)
    await cache.set("key", "new_value", version=2)
    
    # Check if key exists
    if await cache.has_key("key"):
        value = await cache.get("key")
```


## Redis Cache

Unfazed provides two Redis cache backends: native client and serialized client.

### Native Redis Client

The native Redis client (`DefaultBackend`) completely inherits from `redis-py`'s `Redis` class, supporting all Redis commands.

#### Features

- **Complete Redis Support**: Supports all Redis commands and features
- **Connection Pool Management**: Automatic connection pool and health checks
- **SSL/TLS Support**: Supports secure connections
- **Retry Mechanism**: Automatic retry and error handling
- **Key Prefix**: Manual key prefix management

#### Configuration

```python
UNFAZED_SETTINGS = {
    "CACHE": {
        "redis": {
            "BACKEND": "unfazed.cache.backends.redis.defaultclient.DefaultBackend",
            "LOCATION": "redis://username:password@localhost:6379/0",
            "OPTIONS": {
                "PREFIX": "app_cache",
                "MAX_CONNECTIONS": 20,
                "HEALTH_CHECK_INTERVAL": 30,
                "SOCKET_TIMEOUT": 5.0,
                "SOCKET_CONNECT_TIMEOUT": 2.0,
                "RETRY_ON_TIMEOUT": True,
                "RETRY_ON_ERROR": True,
                "SSL": False,
            },
        },
    }
}
```

#### Usage Example

```python
from unfazed.cache import caches
from unfazed.cache.backends.redis.defaultclient import DefaultBackend

async def redis_usage():
    cache: DefaultBackend = caches["redis"]
    
    # Basic operations
    await cache.set("key", "value")
    value = await cache.get("key")
    
    # Use key prefix
    prefixed_key = cache.make_key("user:1")
    await cache.set(prefixed_key, {"name": "John"})
    
    # Redis specific features
    await cache.client.hset("user:1", "name", "Jane")
    await cache.client.hset("user:1", "age", "30")
    user_data = await cache.client.hgetall("user:1")
    
    # List operations
    await cache.client.lpush("queue", "item1")
    await cache.client.lpush("queue", "item2")
    item = await cache.client.rpop("queue")
    
    # Set operations
    await cache.client.sadd("users", "user1", "user2")
    users = await cache.client.smembers("users")
    
    # Sorted sets
    await cache.client.zadd("scores", {"alice": 100, "bob": 90})
    top_scores = await cache.client.zrevrange("scores", 0, 2, withscores=True)
```

#### Notes

- **Key Isolation**: Manual key prefix management needed in production to avoid key conflicts
- **Serialization**: Only supports string and byte data, complex objects need manual serialization
- **Connection Management**: Supports async context manager for automatic connection management

### Serialized Redis Client

The serialized Redis client (`SerializerBackend`) is a wrapper around the native client, providing automatic serialization and compression features.

#### Features

- **Automatic Serialization**: Support for storing Python objects (dict, list, set, tuple, etc.)
- **Compression Support**: Optional zlib compression to reduce storage space
- **Type Preservation**: Maintains original data types
- **Key Prefix**: Automatic key prefix management
- **Counter Support**: Support for incr/decr operations

#### Configuration

```python
UNFAZED_SETTINGS = {
    "CACHE": {
        "redis_serialized": {
            "BACKEND": "unfazed.cache.backends.redis.serializedclient.SerializerBackend",
            "LOCATION": "redis://localhost:6379/0",
            "OPTIONS": {
                "PREFIX": "app_cache",
                "SERIALIZER": "unfazed.cache.serializers.pickle.PickleSerializer",
                "COMPRESSOR": "unfazed.cache.compressors.zlib.ZlibCompressor",
                "MAX_CONNECTIONS": 10,
                "HEALTH_CHECK_INTERVAL": 30,
            },
        },
    }
}
```

#### Usage Example

```python
from unfazed.cache import caches
from unfazed.cache.backends.redis.serializedclient import SerializerBackend

async def serialized_redis_usage():
    cache: SerializerBackend = caches["redis_serialized"]
    
    # Store complex objects
    user_data = {
        "name": "John",
        "age": 28,
        "hobbies": ["reading", "swimming", "programming"],
        "profile": {
            "email": "john@example.com",
            "phone": "13800138000"
        }
    }
    
    await cache.set("user:1", user_data, timeout=3600)
    
    # Store lists
    await cache.set("numbers", [1, 2, 3, 4, 5])
    
    # Store sets
    await cache.set("tags", {"python", "fastapi", "redis"})
    
    # Counter operations
    await cache.set("visits", 0)
    await cache.incr("visits")
    await cache.incr("visits", 5)
    
    # Get data
    user = await cache.get("user:1")
    numbers = await cache.get("numbers")
    tags = await cache.get("tags")
    visits = await cache.get("visits")
    
    # Check if key exists
    if await cache.has_key("user:1"):
        print("User data exists")
    
    # Delete key
    await cache.delete("user:1")
```

#### Notes

- **Concurrency Safety**: Recommend using with locking mechanisms in production
- **Serialization Limitations**: Doesn't support certain special objects (like file handles, network connections)
- **Performance Considerations**: Serialization and compression add CPU overhead
- **Storage Space**: Compression can significantly reduce storage space, especially for repetitive data

## Serialization and Compression

### Serializers

Unfazed provides an extensible serializer interface, defaulting to Pickle serializer.

#### Built-in Serializers

```python
# Pickle serializer (default)
from unfazed.cache.serializers.pickle import PickleSerializer

# Custom serializer
from unfazed.protocol import SerializerBase
import json

class JSONSerializer(SerializerBase):
    def dumps(self, value):
        return json.dumps(value).encode('utf-8')
    
    def loads(self, value):
        return json.loads(value.decode('utf-8'))
```

#### Configuring Custom Serializers

```python
UNFAZED_SETTINGS = {
    "CACHE": {
        "custom": {
            "BACKEND": "unfazed.cache.backends.redis.serializedclient.SerializerBackend",
            "LOCATION": "redis://localhost:6379/0",
            "OPTIONS": {
                "SERIALIZER": "myapp.serializers.JSONSerializer",
                "PREFIX": "custom_cache",
            },
        },
    }
}
```

### Compressors

Unfazed provides an extensible compressor interface, defaulting to zlib compressor.

#### Built-in Compressors

```python
# Zlib compressor (default)
from unfazed.cache.compressors.zlib import ZlibCompressor

# Custom compressor
from unfazed.protocol import CompressorBase
import lz4

class LZ4Compressor(CompressorBase):
    def compress(self, value):
        return lz4.compress(value)
    
    def decompress(self, value):
        return lz4.decompress(value)
```

#### Configuring Custom Compressors

```python
UNFAZED_SETTINGS = {
    "CACHE": {
        "compressed": {
            "BACKEND": "unfazed.cache.backends.redis.serializedclient.SerializerBackend",
            "LOCATION": "redis://localhost:6379/0",
            "OPTIONS": {
                "SERIALIZER": "unfazed.cache.serializers.pickle.PickleSerializer",
                "COMPRESSOR": "myapp.compressors.LZ4Compressor",
                "PREFIX": "compressed_cache",
            },
        },
    }
}
```

## Cache Decorators

Unfazed provides a powerful `@cached` decorator that supports both async and sync function caching.

### Basic Usage

```python
from unfazed.cache.decorators import cached

# Basic caching
@cached(timeout=300)
async def get_user_info(user_id: int) -> dict:
    # Simulate database query
    return {"user_id": user_id, "name": "John", "age": 25}

# Use specific cache backend
@cached(using="redis", timeout=600)
async def get_product_info(product_id: int) -> dict:
    return {"product_id": product_id, "name": "Product A", "price": 99.99}

# Specify cache key parameters
@cached(timeout=1800, include=["user_id", "category"])
async def get_user_preferences(user_id: int, category: str, page: int = 1) -> list:
    return [{"pref_id": 1, "category": category, "user_id": user_id}]
```

### Advanced Usage

```python
from unfazed.cache.decorators import cached

# Multi-layer cache strategy
@cached(using="local_memory", timeout=60)      # Local cache 1 minute
@cached(using="redis", timeout=3600)           # Redis cache 1 hour
async def get_expensive_data(key: str) -> dict:
    # Simulate expensive computation or database query
    return {"key": key, "data": "expensive_result", "timestamp": time.time()}

# Conditional caching
@cached(timeout=300)
async def get_conditional_data(user_id: int, force_refresh: bool = False) -> dict:
    if force_refresh:
        # Force cache refresh
        return await get_conditional_data(user_id, force_update=True)
    
    return {"user_id": user_id, "data": "cached_result"}

# Custom cache keys
@cached(timeout=600, include=["user_id", "role"])
async def get_user_permissions(user_id: int, role: str, context: str = "default") -> list:
    # context parameter won't affect cache key
    return [f"permission_{role}_{context}"]
```

### Decorator Features

- **Async Support**: Full support for async functions
- **Sync Support**: Automatically wraps sync functions as async (using `run_in_threadpool`)
- **Parameter Filtering**: Option to select specific parameters as cache keys
- **Force Update**: Support `force_update=True` to bypass cache
- **Key Generation**: Automatically generate cache keys based on function signatures (format: `module:function_name:param1_value:param2_value`)
- **Error Handling**: Graceful handling of cache errors
- **Warning Prompts**: Issue warnings for positional argument usage, recommend using keyword arguments

## Best Practices

### 1. Cache Strategy Design

```python
# Layered cache strategy
@cached(using="local_memory", timeout=30)    # Hot data local cache
@cached(using="redis", timeout=3600)         # Stable data Redis cache
async def get_user_profile(user_id: int) -> dict:
    return await fetch_user_from_database(user_id)

# Cache prewarming
async def warm_up_cache():
    user_ids = [1, 2, 3, 4, 5]
    for user_id in user_ids:
        await get_user_profile(user_id)
```


### 2. Performance Optimization

```python
# Batch operations
async def batch_cache_operations():
    cache = caches["redis"]
    
    # Batch set
    pipeline = cache.client.pipeline()
    for i in range(100):
        pipeline.set(f"key_{i}", f"value_{i}")
    await pipeline.execute()
    
    # Batch get
    keys = [f"key_{i}" for i in range(100)]
    values = await cache.client.mget(keys)

# Async concurrency
import asyncio

async def concurrent_cache_operations():
    cache = caches["default"]
    
    # Concurrent set multiple keys
    tasks = [
        cache.set(f"key_{i}", f"value_{i}")
        for i in range(10)
    ]
    await asyncio.gather(*tasks)
```
