import os

import pytest

from unfazed.cache.backends.redis import AsyncDefaultBackend

HOST = os.getenv("REDIS_HOST", "redis")


@pytest.fixture
async def client():
    client: AsyncDefaultBackend = AsyncDefaultBackend(
        f"redis://{HOST}:6379", options={"PREFIX": "test"}
    )

    yield client

    await client.close()


async def test_client_init():
    client = AsyncDefaultBackend(f"redis://{HOST}:6379")

    await client.flushdb()
    await client.set("foo", "bar")

    await client.close()

    # test retry
    client = AsyncDefaultBackend(f"redis://{HOST}:6379", options={"retry": False})

    client.client.get_retry() is None
    await client.close()

    # test serializer is None
    async with AsyncDefaultBackend(
        f"redis://{HOST}:6379",
        options={"SERIALIZER": None, "COMPRESSOR": None},
    ) as client:
        await client.set("foo", "bar")
        assert await client.get("foo") == "bar"

    with pytest.raises(ValueError):
        AsyncDefaultBackend(f"redis://{HOST}:6379", options={"SERIALIZER": None})

    # no prefix
    async with AsyncDefaultBackend(
        f"redis://{HOST}:6379", options={"PREFIX": None}
    ) as client:
        await client.set("foo", "bar")
        assert await client.get("foo") == "bar"

    # test sp_client
    async with AsyncDefaultBackend(
        f"redis://{HOST}:6379", options={"decode_responses": False}
    ) as client:
        assert client.have_sp_client is False


async def test_generic_cmd(client: AsyncDefaultBackend):
    await client.flushdb()

    await client.ping()

    await client.set("foo", "bar")
    assert await client.exists("foo") == 1
    assert await client.exists("foo1") == 0

    await client.expire("foo", 1)
    assert await client.ttl("foo") <= 1

    assert await client.touch("foo", "foo1") == 1


async def test_str_cmd(client: AsyncDefaultBackend):
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


async def test_raw_str_cmd(client: AsyncDefaultBackend):
    await client.flushdb()

    await client.raw_set("foo", "bar")
    assert await client.raw_get("foo") == "bar"

    # append
    await client.append("foo", "baz")
    assert await client.raw_get("foo") == "barbaz"

    # getrange
    assert await client.getrange("foo", 0, 2) == "bar"

    # setrange
    await client.setrange("foo", 3, "zab")
    assert await client.raw_get("foo") == "barzab"

    # strlen
    assert await client.strlen("foo") == 6

    # substr
    assert await client.substr("foo", 0, 2) == "bar"


async def test_int_float_cmd(client: AsyncDefaultBackend):
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


async def test_hash_cmd(client: AsyncDefaultBackend) -> None:
    await client.flushdb()

    await client.hset("set1", mapping={"foo": "bar", "baz": 1})
    assert await client.hget("set1", "foo") == "bar"
