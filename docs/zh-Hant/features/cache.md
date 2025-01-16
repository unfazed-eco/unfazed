Unfazed 缓存
=====

unfazed 提供了两种缓存类型，包括 memory 和 redis。其中 redis 支持原生 redis client 和序列化 redis client。


## 进程内缓存

进程内缓存，用于存储一些短期数据。

1、配置

```python

# settings.py

UNFAZED_SETTINGS = {
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "unfazed_cache1",
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
                "PREFIX": "unfazed_cache1",
            },
        },
    }
}

```


2、使用

```python

from unfazed.cache import caches
from unfazed.cache.backends.locmem import LocMemCache

async def test_cache():

    cache: LocMemCache = caches['default']

    await cache.set("key", "value", timeout=60)

    value = await cache.get("key")


```


其他方法见 [local memory cache](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/cache/backends/locmem.py)



## Redis 缓存

### 原生 redis client

原生 redis client 完全继承 `redis-py` 中的 `Redis`，可以直接使用 `redis-py` 的方法。
在生产环境中使用该 client 时，需要注意键值隔离的问题，所以如果需要前缀，手动调用 `make_key` 方法。
在 unfazed-eco 生态中，规划了 `unfazed-redis` 项目，用于解决键值隔离的问题。

1、配置

```python

# settings.py

UNFAZED_SETTINGS = {
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.redis.defaultclient.DefaultBackend", 
            "LOCATION": "redis://redis:6379/0",
            "OPTIONS": {
                "PREFIX": "unfazed_cache1",
            }
        },
    }
}

```

2、使用

```python

from unfazed.cache import caches
from unfazed.cache.backends.redis.defaultclient import DefaultBackend


async def test_cache():

    cache: DefaultBackend = caches['default']

    await cache.set("key", "value")

    maked_key = cache.make_key("key")
    await cache.set(maked_key, "value")

    value = await cache.get("key")
    maked_value = await cache.get(maked_key)


```

其他方法见 [redis-py command](https://redis-py.readthedocs.io/en/stable/commands.html)


### 序列化 redis client

序列化 redis client 是对原生 redis client 的封装，提供了序列化和反序列化以及压缩和解压缩的功能。设计思路来自于 django-redis。

序列化 redis client 可以使用 set/get 方法直接存储以及获取能够被序列化的对象。比如 dict、list、set、tuple 等。

在生产环境中使用该 client 时，需要注意并发问题。需要配合 `lock` 使用。


1、配置

```python

# settings.py

UNFAZED_SETTINGS = {
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.redis.serializedclient.SerializedBackend",
            "LOCATION": "redis://redis:6379/0",
            "OPTIONS": {
                "PREFIX": "unfazed_cache1",
                "SERIALIZER": "unfazed.cache.serializers.pickle.PickleSerializer",
                "COMPRESSOR": "unfazed.cache.compressors.zlib.ZlibCompressor",
            }
        },
    }
}

```


2、使用

```python

from unfazed.cache import caches
from unfazed.cache.backends.redis.serializedclient import SerializedBackend

async def test_cache():

    cache: SerializedBackend = caches['default']

    await cache.set("key", {"foo": "bar"})

    value = await cache.get("key")

```

其他方法见 [serializedclient](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/cache/backends/redis/serializedclient.py)


## cached 装饰器

unfazed 提供了 cached 装饰器，用于缓存异步函数的返回值。

1、使用

```python

from unfazed.cache.decorators import cached

# 基础用法
@cached()
async def test_cache():
    return "value"


test_cache() # "value"



# 更换缓存位置
@cached(cache="default")
async def test_cache():
    return "value"

test_cache() # "value"



# 更换缓存超时时间

@cached(timeout=60)
async def test_cache():
    return "value"

test_cache() # "value"



# 更换缓存键
# 该方法会将 a 和 b 作为键，所以 a 和 b 的值不同，会返回不同的结果
# 注意传递的参数必须是关键字参数
@cached(include=["a", "b"])
async def test_cache(a, b):
    return a + b

test_cache(a=1, b=2) # 3

# 错误使用
test_cache(1, 2)


# 同步函数
@cached()
def test_cache():
    return "value"


# 强制更新

@cached()
async def test_cache():
    return "value"

await test_cache() # "value"
await test_cache(force_update=True) # "value"

```

2、叠加使用


在一些大 key、更新频率低、使用频率高的情况下，可以使用叠加 cached 的方式，减少 redis 压力。

```python


@cached(using="local_memory", timeout=10)
@cached(using="redis", timeout=60)
async def test_cache():
    return "huge value"


```


