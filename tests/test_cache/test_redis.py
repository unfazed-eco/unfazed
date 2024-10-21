
import os

import pytest

from unfazed.cache.backends.redis import AsyncDefaultBackend


async def test_redis_client():
    redis_host = os.environ.get("REDIS_HOST", "redis")
    async with AsyncDefaultBackend(location=f"redis://{redis_host}:6379") as client:
        await client.flushdb()

        await client.set("foo", "bar")
        assert await client.get("foo") == "bar"

        await client.set("foo1", 10)
        assert await client.decrby("foo1", 5) == 5
        assert int(await client.get("foo1")) == 5
