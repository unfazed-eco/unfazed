import os

import pytest

from unfazed.cache.backends.redis import SerializerBackend

HOST = os.getenv("REDIS_HOST", "redis")


@pytest.fixture
async def client():
    client: SerializerBackend = SerializerBackend(
        f"redis://{HOST}:6379", options={"PREFIX": "test"}
    )

    yield client

    await client.close()


async def test_client_init():
    client = SerializerBackend(f"redis://{HOST}:6379")

    await client.flushdb()
    await client.set("foo", "bar")

    await client.close()

    # test retry
    client = SerializerBackend(f"redis://{HOST}:6379", options={"retry": False})

    client.client.get_retry() is None
    await client.close()

    # test serializer is None
    async with SerializerBackend(
        f"redis://{HOST}:6379",
        options={"SERIALIZER": None, "COMPRESSOR": None},
    ) as client:
        await client.set("foo", "bar")
        assert await client.get("foo") == b"bar"

    with pytest.raises(ValueError):
        SerializerBackend(f"redis://{HOST}:6379", options={"SERIALIZER": None})

    # no prefix
    async with SerializerBackend(
        f"redis://{HOST}:6379", options={"PREFIX": None}
    ) as client:
        await client.set("foo", "bar")
        assert await client.get("foo") == "bar"

    with pytest.raises(ValueError):
        SerializerBackend(f"redis://{HOST}:6379", options={"decode_responses": True})


async def test_generic_cmd(client: SerializerBackend):
    await client.flushdb()

    await client.set("foo", "bar")
    assert await client.exists("foo") == 1
    assert await client.exists("foo1") == 0

    await client.expire("foo", 1)
    assert await client.ttl("foo") <= 1

    assert await client.touch("foo", "foo1") == 1


async def test_str_cmd(client: SerializerBackend):
    await client.flushdb()

    await client.set("foo", "bar")
    assert await client.get("foo") == "bar"

    class A:
        pass

    await client.set("foo1", 1)
    assert await client.get("foo1") == 1

    

    await client.setex("foo2", 1, 1.1)
    assert await client.get("foo2") == 1.1

    await client.setnx("foo3", {"a": 1, "b": [2]})
    assert await client.get("foo3") == {"a": 1, "b": [2]}

    # getdel
    await client.set("foo4", "bar")
    assert await client.getdel("foo4") == "bar"
    assert await client.get("foo4") is None

    # getex
    await client.set("foo5", "bar")
    assert await client.getex("foo5", ex=2)
    assert await client.ttl("foo5") <= 2

    # mset + mget
    await client.mset({"foo6": "bar", "foo7": {"a": 1, "b": [2]}})
    await client.msetnx({"foo8": 1})
    assert await client.mget(["foo6", "foo7", "foo8"]) == ["bar", {"a": 1, "b": [2]}, 1]

    # psetex
    await client.psetex("foo9", 1000, "bar")
    assert await client.get("foo9") == "bar"

    # getset
    await client.set("foo10", "bar")
    assert await client.getset("foo10", "baz") == "bar"
    assert await client.get("foo10") == "baz"


async def test_int_float_cmd(client: SerializerBackend):
    await client.flushdb()

    await client.set("foo", 1)
    assert await client.get("foo") == 1

    await client.incr("foo")
    assert await client.get("foo") == 2

    await client.incrby("foo", 2)
    assert await client.get("foo") == 4

    await client.decr("foo")
    assert await client.get("foo") == 3

    await client.decrby("foo", 2)
    assert await client.get("foo") == 1

    await client.incrbyfloat("foo", 1.1)
    assert await client.get("foo") == 2.1
