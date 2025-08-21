# Unfazed 缓存系统

Unfazed 提供了完整的缓存解决方案，支持多种缓存后端，包括进程内内存缓存和 Redis 缓存。缓存系统设计灵活，支持序列化、压缩、键前缀、版本控制等高级功能。

更高级的 redis client 见 [unfazed-redis](https://github.com/unfazed-eco/unfazed-redis)


带监控的 redis client 见 [unfazed-prometheus](https://github.com/unfazed-eco/unfazed-prometheus)



## 核心特性

- **多后端支持**: 进程内内存缓存和 Redis 缓存
- **异步操作**: 全异步 API 设计，支持高并发
- **序列化支持**: 自动序列化复杂 Python 对象
- **压缩支持**: 可选的 zlib 压缩，减少存储空间
- **键管理**: 支持键前缀、版本控制、自动过期
- **装饰器支持**: `@cached` 装饰器简化缓存使用

## 缓存处理器

Unfazed 缓存系统使用 `CacheHandler` 类管理多个缓存后端，提供统一的接口。

### 核心组件

- **caches**: 全局缓存处理器实例，管理所有配置的缓存后端
- **CacheHandler**: 继承自 `Storage[CacheBackend]`，提供缓存生命周期管理


### 使用方式

```python
from unfazed.cache import caches

# 获取默认缓存
default_cache = caches["default"]

# 获取特定缓存
redis_cache = caches["redis"]

```

## 快速开始

### 1. 基本配置

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

### 2. 基本使用

```python
from unfazed.cache import caches

async def basic_usage():
    # 获取缓存实例
    cache = caches["default"]
    
    # 设置缓存
    await cache.set("user:1", "value", timeout=3600)
    
    # 获取缓存
    user = await cache.get("user:1")
    
    # 检查键是否存在
    exists = await cache.has_key("user:1")
    
    # 删除缓存
    await cache.delete("user:1")
    
    # 清空所有缓存
    await cache.clear()
```

## 进程内内存缓存

进程内内存缓存 (`LocMemCache`) 适用于单进程应用，提供高性能的内存存储。

### 特性

- **线程安全**: 使用 asyncio Lock 保证并发安全
- **自动清理**: 支持 TTL 和最大条目数限制
- **LRU 策略**: 使用 OrderedDict 实现 LRU 缓存淘汰
- **版本控制**: 支持键版本管理
- **键前缀**: 支持键名前缀隔离

### 配置选项

```python
UNFAZED_SETTINGS = {
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "app_cache",  # 缓存实例唯一标识
            "OPTIONS": {
                "PREFIX": "app",      # 键前缀
                "VERSION": 1,         # 默认版本号
                "MAX_ENTRIES": 1000,  # 最大缓存条目数
            },
        },
    }
}
```

### 高级用法

```python
from unfazed.cache import caches
from unfazed.cache.backends.locmem import LocMemCache

async def advanced_locmem_usage():
    cache: LocMemCache = caches["default"]
    
    # 计数器操作
    await cache.set("counter", 0)
    await cache.incr("counter")      # 增加 1
    await cache.incr("counter", 5)   # 增加 5
    await cache.decr("counter", 2)   # 减少 2
    
    # 版本控制
    await cache.set("key", "value", version=1)
    await cache.set("key", "new_value", version=2)
    
    # 检查键是否存在
    if await cache.has_key("key"):
        value = await cache.get("key")
```


## Redis 缓存

Unfazed 提供两种 Redis 缓存后端：原生客户端和序列化客户端。

### 原生 Redis 客户端

原生 Redis 客户端 (`DefaultBackend`) 完全继承 `redis-py` 的 `Redis` 类，支持所有 Redis 命令。

#### 特性

- **完整 Redis 支持**: 支持所有 Redis 命令和功能
- **连接池管理**: 自动连接池和健康检查
- **SSL/TLS 支持**: 支持安全连接
- **重试机制**: 自动重试和错误处理
- **键前缀**: 手动键前缀管理

#### 配置

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

#### 使用示例

```python
from unfazed.cache import caches
from unfazed.cache.backends.redis.defaultclient import DefaultBackend

async def redis_usage():
    cache: DefaultBackend = caches["redis"]
    
    # 基本操作
    await cache.set("key", "value")
    value = await cache.get("key")
    
    # 使用键前缀
    prefixed_key = cache.make_key("user:1")
    await cache.set(prefixed_key, {"name": "李四"})
    
    # Redis 特定功能
    await cache.client.hset("user:1", "name", "王五")
    await cache.client.hset("user:1", "age", "30")
    user_data = await cache.client.hgetall("user:1")
    
    # 列表操作
    await cache.client.lpush("queue", "item1")
    await cache.client.lpush("queue", "item2")
    item = await cache.client.rpop("queue")
    
    # 集合操作
    await cache.client.sadd("users", "user1", "user2")
    users = await cache.client.smembers("users")
    
    # 有序集合
    await cache.client.zadd("scores", {"alice": 100, "bob": 90})
    top_scores = await cache.client.zrevrange("scores", 0, 2, withscores=True)
```

#### 注意事项

- **键隔离**: 在生产环境中需要手动管理键前缀，避免键冲突
- **序列化**: 只支持字符串和字节数据，复杂对象需要手动序列化
- **连接管理**: 支持异步上下文管理器，自动连接管理

### 序列化 Redis 客户端

序列化 Redis 客户端 (`SerializerBackend`) 是对原生客户端的封装，提供自动序列化和压缩功能。

#### 特性

- **自动序列化**: 支持存储 Python 对象（dict、list、set、tuple 等）
- **压缩支持**: 可选的 zlib 压缩，减少存储空间
- **类型保持**: 保持原始数据类型
- **键前缀**: 自动键前缀管理
- **计数器支持**: 支持 incr/decr 操作

#### 配置

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

#### 使用示例

```python
from unfazed.cache import caches
from unfazed.cache.backends.redis.serializedclient import SerializerBackend

async def serialized_redis_usage():
    cache: SerializerBackend = caches["redis_serialized"]
    
    # 存储复杂对象
    user_data = {
        "name": "赵六",
        "age": 28,
        "hobbies": ["读书", "游泳", "编程"],
        "profile": {
            "email": "zhaoliu@example.com",
            "phone": "13800138000"
        }
    }
    
    await cache.set("user:1", user_data, timeout=3600)
    
    # 存储列表
    await cache.set("numbers", [1, 2, 3, 4, 5])
    
    # 存储集合
    await cache.set("tags", {"python", "fastapi", "redis"})
    
    # 计数器操作
    await cache.set("visits", 0)
    await cache.incr("visits")
    await cache.incr("visits", 5)
    
    # 获取数据
    user = await cache.get("user:1")
    numbers = await cache.get("numbers")
    tags = await cache.get("tags")
    visits = await cache.get("visits")
    
    # 检查键是否存在
    if await cache.has_key("user:1"):
        print("用户数据存在")
    
    # 删除键
    await cache.delete("user:1")
```

#### 注意事项

- **并发安全**: 在生产环境中建议配合锁机制使用
- **序列化限制**: 不支持某些特殊对象（如文件句柄、网络连接等）
- **性能考虑**: 序列化和压缩会增加 CPU 开销
- **存储空间**: 压缩可以显著减少存储空间，特别是对于重复数据

## 序列化和压缩

### 序列化器

Unfazed 提供了可扩展的序列化器接口，默认使用 Pickle 序列化器。

#### 内置序列化器

```python
# Pickle 序列化器（默认）
from unfazed.cache.serializers.pickle import PickleSerializer

# 自定义序列化器
from unfazed.protocol import SerializerBase
import json

class JSONSerializer(SerializerBase):
    def dumps(self, value):
        return json.dumps(value).encode('utf-8')
    
    def loads(self, value):
        return json.loads(value.decode('utf-8'))
```

#### 配置自定义序列化器

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

### 压缩器

Unfazed 提供了可扩展的压缩器接口，默认使用 zlib 压缩器。

#### 内置压缩器

```python
# Zlib 压缩器（默认）
from unfazed.cache.compressors.zlib import ZlibCompressor

# 自定义压缩器
from unfazed.protocol import CompressorBase
import lz4

class LZ4Compressor(CompressorBase):
    def compress(self, value):
        return lz4.compress(value)
    
    def decompress(self, value):
        return lz4.decompress(value)
```

#### 配置自定义压缩器

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

## 缓存装饰器

Unfazed 提供了强大的 `@cached` 装饰器，支持异步和同步函数缓存。

### 基本用法

```python
from unfazed.cache.decorators import cached

# 基础缓存
@cached(timeout=300)
async def get_user_info(user_id: int) -> dict:
    # 模拟数据库查询
    return {"user_id": user_id, "name": "张三", "age": 25}

# 使用特定缓存后端
@cached(using="redis", timeout=600)
async def get_product_info(product_id: int) -> dict:
    return {"product_id": product_id, "name": "商品A", "price": 99.99}

# 指定缓存键参数
@cached(timeout=1800, include=["user_id", "category"])
async def get_user_preferences(user_id: int, category: str, page: int = 1) -> list:
    return [{"pref_id": 1, "category": category, "user_id": user_id}]
```

### 高级用法

```python
from unfazed.cache.decorators import cached

# 多层缓存策略
@cached(using="local_memory", timeout=60)      # 本地缓存 1 分钟
@cached(using="redis", timeout=3600)           # Redis 缓存 1 小时
async def get_expensive_data(key: str) -> dict:
    # 模拟昂贵的计算或数据库查询
    return {"key": key, "data": "expensive_result", "timestamp": time.time()}

# 条件缓存
@cached(timeout=300)
async def get_conditional_data(user_id: int, force_refresh: bool = False) -> dict:
    if force_refresh:
        # 强制刷新缓存
        return await get_conditional_data(user_id, force_update=True)
    
    return {"user_id": user_id, "data": "cached_result"}

# 缓存键自定义
@cached(timeout=600, include=["user_id", "role"])
async def get_user_permissions(user_id: int, role: str, context: str = "default") -> list:
    # context 参数不会影响缓存键
    return [f"permission_{role}_{context}"]
```

### 装饰器特性

- **异步支持**: 完全支持异步函数
- **同步支持**: 自动将同步函数包装为异步（使用 `run_in_threadpool`）
- **参数过滤**: 可选择特定参数作为缓存键
- **强制更新**: 支持 `force_update=True` 绕过缓存
- **键生成**: 自动生成基于函数签名的缓存键（格式：`module:function_name:param1_value:param2_value`）
- **错误处理**: 优雅处理缓存错误
- **警告提示**: 对位置参数使用发出警告，建议使用关键字参数

## 最佳实践

### 1. 缓存策略设计

```python
# 分层缓存策略
@cached(using="local_memory", timeout=30)    # 热点数据本地缓存
@cached(using="redis", timeout=3600)         # 稳定数据 Redis 缓存
async def get_user_profile(user_id: int) -> dict:
    return await fetch_user_from_database(user_id)

# 缓存预热
async def warm_up_cache():
    user_ids = [1, 2, 3, 4, 5]
    for user_id in user_ids:
        await get_user_profile(user_id)
```


### 2. 性能优化

```python
# 批量操作
async def batch_cache_operations():
    cache = caches["redis"]
    
    # 批量设置
    pipeline = cache.client.pipeline()
    for i in range(100):
        pipeline.set(f"key_{i}", f"value_{i}")
    await pipeline.execute()
    
    # 批量获取
    keys = [f"key_{i}" for i in range(100)]
    values = await cache.client.mget(keys)

# 异步并发
import asyncio

async def concurrent_cache_operations():
    cache = caches["default"]
    
    # 并发设置多个键
    tasks = [
        cache.set(f"key_{i}", f"value_{i}")
        for i in range(10)
    ]
    await asyncio.gather(*tasks)
```
