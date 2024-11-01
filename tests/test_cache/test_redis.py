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

    await client.set("foo1", 1)
    assert await client.get("foo1") == 1

    await client.set("foo2", 1.1)
    assert await client.get("foo2") == 1.1

    await client.set("foo3", {"a": 1, "b": [2]})
    assert await client.get("foo3") == {"a": 1, "b": [2]}
