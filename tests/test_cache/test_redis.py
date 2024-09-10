import pytest

from unfazed.cache.backends.redis import AsyncDefaultBackend


@pytest.mark.asyncio
async def test_redis_client():
    async with AsyncDefaultBackend(location="redis://redis:6379") as client:
        await client.flushdb()

        await client.set("foo", "bar")
        assert await client.get("foo") == "bar"

        await client.set("foo1", 10)
        assert await client.decrby("foo1", 5) == 5
        assert int(await client.get("foo1")) == 5
