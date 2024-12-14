import os

import pytest

from unfazed.cache.backends.redis import DefaultBackend

HOST = os.getenv("REDIS_HOST", "redis")


async def test_redis_cmd() -> None:
    # default client with options
    client1 = DefaultBackend(
        f"redis://{HOST}:6379",
        options={"PREFIX": "test_default_backend_cmd", "decode_responses": True},
    )
    await client1.flushdb()

    key1 = client1.make_key("key1")

    assert key1 == "test_default_backend_cmd:key1"

    await client1.set(key1, "value")
    assert await client1.get(key1) == "value"

    with pytest.raises(AttributeError):
        await client1.nonexist_cmd(key1)

    await client1.close()

    # default client without options
    # and use async with
    async with DefaultBackend(f"redis://{HOST}:6379") as client2:
        key2 = client2.make_key("key2")
        await client2.set(key2, "value")

    # default client with retry
    async with DefaultBackend(
        f"redis://{HOST}:6379",
        options={"retry": False},
    ) as client3:
        key3 = client3.make_key("key3")
        await client3.set(key3, "value")
