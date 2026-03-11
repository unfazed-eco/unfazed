Unfazed 缓存
============

Unfazed 内置可插拔的缓存框架，让你通过简单的异步 API 存储和检索数据。你可以配置多个命名的缓存后端 —— 开发时用本地内存，生产环境用 Redis —— 并通过单一配置切换。还提供 `@cached` 装饰器，用于自动缓存函数返回值。

## 快速开始

### 1. 在配置中添加缓存后端

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

### 2. 使用缓存

```python
from unfazed.cache import caches

cache = caches["default"]

await cache.set("greeting", "hello", timeout=60)
value = await cache.get("greeting")  # "hello"
```

## 配置

`CACHE` 配置是一个字典，每个键是缓存别名（如 `"default"`、`"sessions"`），每个值描述后端：

```python
"CACHE": {
    "<alias>": {
        "BACKEND": "<dotted.path.to.BackendClass>",
        "LOCATION": "<backend-specific location>",
        "OPTIONS": { ... },
    },
}
```

| 字段 | 描述 |
|-------|-------------|
| `BACKEND` | 缓存后端类的点分导入路径。 |
| `LOCATION` | 后端特定的位置。LocMem：唯一名称字符串。Redis：连接 URL，如 `redis://localhost:6379/0`。 |
| `OPTIONS` | 后端特定选项的字典（见下文各后端）。 |

你可以定义任意多个命名缓存，并通过别名访问：

```python
default = caches["default"]
sessions = caches["sessions"]
```

## 内置后端

### LocMemCache — 本地内存

基于 `OrderedDict` 的简单进程内缓存。适用于开发和单进程部署。进程重启后数据会丢失。

**后端路径：** `unfazed.cache.backends.locmem.LocMemCache`

**选项：**

| 选项 | 类型 | 默认值 | 描述 |
|--------|------|---------|-------------|
| `PREFIX` | `str` | location 值 | 用于命名空间隔离的键前缀。 |
| `VERSION` | `int` | `None` | 追加到键的默认版本号。 |
| `MAX_ENTRIES` | `int` | `300` | 最大条目数。满时淘汰最旧的条目。 |

**配置示例：**

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

### DefaultBackend — 原生 Redis

`redis.asyncio.Redis` 的轻量封装，增加键前缀和连接管理。所有标准 Redis 命令通过属性代理可用 —— 你直接在后端实例上调用 Redis 方法。

**后端路径：** `unfazed.cache.backends.redis.DefaultBackend`

**配置示例：**

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

### SerializerBackend — 带序列化的 Redis

在 Redis 基础上增加自动序列化和可选压缩，可透明存储复杂 Python 对象（dict、list、dataclass 等）。默认使用 Pickle + Zlib。

**后端路径：** `unfazed.cache.backends.redis.SerializerBackend`

**配置示例：**

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

**Redis OPTIONS 参考**（适用于 `DefaultBackend` 和 `SerializerBackend`）：

| 选项 | 类型 | 默认值 | 描述 |
|--------|------|---------|-------------|
| `PREFIX` | `str` | `None` | 用于命名空间隔离的键前缀。 |
| `SERIALIZER` | `str` | `PickleSerializer` | 序列化器类的点分路径（仅 SerializerBackend）。 |
| `COMPRESSOR` | `str` | `ZlibCompressor` | 压缩器类的点分路径（仅 SerializerBackend）。需要序列化器。 |
| `max_connections` | `int` | `10` | 连接池最大连接数。 |
| `decode_responses` | `bool` | `False` | 将 Redis 字节解码为字符串。SerializerBackend 不支持。 |
| `socket_timeout` | `int` | `None` | 套接字超时（秒）。 |
| `socket_connect_timeout` | `int` | `None` | 连接超时（秒）。 |
| `health_check_interval` | `int` | `30` | 健康检查间隔（秒）。 |
| `retry_on_timeout` | `bool` | `False` | 超时错误时重试。 |
| `ssl` | `bool` | `False` | 启用 SSL/TLS。 |

## 示例

### LocMem：基本操作

```python
from unfazed.cache import caches

cache = caches["default"]

# 设置带 5 分钟 TTL 的值
await cache.set("user:1:name", "Alice", timeout=300)

# 获取值（缺失或过期时返回 None）
name = await cache.get("user:1:name")

# 带默认回退的获取
name = await cache.get("user:1:name", default="Anonymous")

# 检查存在性
if await cache.has_key("user:1:name"):
    print("Key exists")

# 删除键
await cache.delete("user:1:name")

# 计数器
await cache.set("hits", 0)
await cache.incr("hits")      # 1
await cache.incr("hits")      # 2
await cache.decr("hits")      # 1

# 清空全部
await cache.clear()
```

### Redis DefaultBackend：完整 Redis API

由于 `DefaultBackend` 将所有属性访问代理到底层 `redis.asyncio.Redis` 客户端，你可以直接使用任何 Redis 命令。只需记得对前缀支持调用 `make_key()`：

```python
from unfazed.cache import caches

cache = caches["default"]  # DefaultBackend 实例

# 字符串操作
await cache.set(cache.make_key("token"), "abc123", ex=3600)
token = await cache.get(cache.make_key("token"))

# 哈希操作
await cache.hset(cache.make_key("user:1"), mapping={"name": "Alice", "role": "admin"})
user = await cache.hgetall(cache.make_key("user:1"))

# 列表操作
await cache.rpush(cache.make_key("queue"), "task1", "task2")
task = await cache.lpop(cache.make_key("queue"))

# 集合操作
await cache.sadd(cache.make_key("tags"), "python", "async")
tags = await cache.smembers(cache.make_key("tags"))
```

### Redis SerializerBackend：存储 Python 对象

`SerializerBackend` 用自动序列化包装字符串命令，可直接存储和检索 Python 对象：

```python
from unfazed.cache import caches

cache = caches["default"]  # SerializerBackend 实例

# 存储 dict — 自动序列化 + 压缩
await cache.set("user:1", {"name": "Alice", "roles": ["admin", "editor"]}, ex=3600)

# 检索 — 自动解压 + 反序列化
user = await cache.get("user:1")  # {"name": "Alice", "roles": ["admin", "editor"]}

# 整型/浮点值不经序列化直接传递
await cache.set("counter", 0)
await cache.incr("counter")   # 1
await cache.decr("counter")   # 0

# 批量操作
await cache.mset({"key1": {"a": 1}, "key2": [1, 2, 3]})
values = await cache.mget(["key1", "key2"])

# 检查 TTL 和存在性
await cache.set("temp", "data", ex=60)
ttl = await cache.ttl("temp")       # 剩余秒数
exists = await cache.exists("temp")  # 存在则为 1
```

### 多后端配置

典型生产配置使用 LocMem 处理临时数据，Redis 处理共享状态：

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

## `@cached` 装饰器

`@cached` 装饰器自动缓存函数返回值。支持异步和同步函数。

```python
from unfazed.cache import cached


@cached(timeout=300)
async def get_user_profile(user_id: int) -> dict:
    # 昂贵的数据库查询
    ...
```

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `using` | `str` | `"default"` | 使用的缓存别名。 |
| `timeout` | `int` | `60` | TTL（秒）。 |
| `include` | `List[str]` | `None` | 参与缓存键的参数名。若为 `None`，则使用所有关键字参数。 |

**缓存键格式：** `module_name:function_name:param1_value:param2_value`

**选择键参数** — 当某些参数不应影响缓存键时使用 `include`：

```python
@cached(timeout=120, include=["user_id"])
async def get_dashboard(user_id: int, request_time: str) -> dict:
    # 仅 user_id 参与缓存键；request_time 被忽略
    ...
```

**使用特定后端：**

```python
@cached(using="local", timeout=60)
async def get_config(key: str) -> str:
    ...
```

**强制刷新缓存** — 传入 `force_update=True` 绕过缓存并存储新结果：

```python
result = await get_user_profile(user_id=42, force_update=True)
```

**注意：** 装饰器仅使用关键字参数生成缓存键。位置参数会被忽略（传入时会发出警告）。

## 自定义序列化器与压缩器

你可以通过实现 `SerializerBase` 或 `CompressorBase` 协议编写类，替换默认的 Pickle/Zlib 实现。

**自定义序列化器：**

```python
# myapp/cache_serializer.py
import json


class JsonSerializer:
    def dumps(self, value: any) -> bytes:
        return json.dumps(value).encode("utf-8")

    def loads(self, value: bytes) -> any:
        return json.loads(value.decode("utf-8"))
```

**自定义压缩器：**

```python
# myapp/cache_compressor.py
import lzma


class LzmaCompressor:
    def compress(self, value: bytes) -> bytes:
        return lzma.compress(value)

    def decompress(self, value: bytes) -> bytes:
        return lzma.decompress(value)
```

**在配置中注册：**

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

## 关闭时清理

在配置中添加内置的 `CacheClear` lifespan，确保服务器关闭时正确关闭所有缓存连接：

```python
"LIFESPAN": [
    "unfazed.cache.lifespan.CacheClear",
]
```

这会在关闭阶段调用 `await caches.close()`，关闭每个已注册的后端。

## API 参考

### CacheHandler（单例：`caches`）

```python
class CacheHandler(Storage[CacheBackend])
```

缓存后端的全局注册表。通过 `caches` 单例访问。

- `caches["alias"]` — 按别名获取后端（缺失时抛出 `KeyError`）。
- `caches["alias"] = backend` — 注册后端。
- `del caches["alias"]` — 移除后端。
- `"alias" in caches` — 检查存在性。
- `async close() -> None`：关闭所有已注册后端。

### LocMemCache

```python
class LocMemCache(location: str, options: Dict[str, Any] | None = None)
```

带自动淘汰的进程内缓存。

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

原生 Redis 后端。通过 `__getattr__` 代理所有 Redis 命令，因此任何 `redis.asyncio.Redis` 方法都可直接使用。

- `make_key(key: str) -> str`：添加配置的前缀。
- `async close() -> None`：关闭 Redis 连接。
- 支持 `async with` 上下文管理器。

### SerializerBackend

```python
class SerializerBackend(location: str, options: Dict[str, Any] | None = None)
```

带透明序列化和压缩的 Redis 后端。

**字符串命令**（序列化）：`get`、`set`、`getdel`、`getex`、`getset`、`mget`、`mset`、`msetnx`、`setex`、`setnx`、`psetex`。

**数值命令**（透传）：`incr`、`incrby`、`incrbyfloat`、`decr`、`decrby`。

**通用命令**：`exists`、`expire`、`touch`、`ttl`、`delete`、`flushdb`。

- `make_key(key: str) -> str`：添加配置的前缀。
- `encode(value: Any) -> int | float | bytes`：序列化并可选压缩值。
- `decode(value: bytes | None) -> Any`：解压并反序列化值。
- `async close() -> None`：关闭 Redis 连接。
- 支持 `async with` 上下文管理器。

### cached

```python
def cached(using: str = "default", timeout: int = 60, include: List[str] | None = None) -> Callable
```

缓存函数返回值的装饰器。支持异步和同步函数。

### CacheClear

```python
class CacheClear(BaseLifeSpan)
```

在关闭时调用 `await caches.close()` 的 lifespan 钩子。

- `async on_shutdown() -> None`：关闭所有缓存后端。
