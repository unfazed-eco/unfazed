import os

from unfazed.cache import caches
from unfazed.cache.backends.redis import AsyncDefaultBackend
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

HOST = os.getenv("REDIS_HOST", "redis")

_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_cache",
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.redis.AsyncDefaultBackend",
            "LOCATION": f"redis://{HOST}:6379",
        },
        "redis1": {
            "BACKEND": "unfazed.cache.backends.redis.AsyncDefaultBackend",
            "LOCATION": f"redis://{HOST}:6379",
            "OPTIONS": {
                "retry": False,
            },
        },
    },
}


async def test_redis_client():
    unfazed = Unfazed(settings=UnfazedSettings(**_Settings))
    await unfazed.setup()

    # default cache
    client: AsyncDefaultBackend = caches["default"]
    await client.flushdb()

    await client.set("foo", "bar")
    assert await client.get("foo") == "bar"

    await client.set("foo1", 10)
    assert await client.decrby("foo1", 5) == 5
    assert int(await client.get("foo1")) == 5

    # close the client
    await client.close()

    # redis1 cache

    client1: AsyncDefaultBackend = caches["redis1"]

    await client1.flushdb()
    await client1.set("foo", "bar")
    assert await client1.get("foo") == "bar"

    await client1.close()
