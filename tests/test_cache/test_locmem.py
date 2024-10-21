import asyncio

import pytest

from unfazed.cache.backends.locmem import LocMemCache


async def test_locmem():
    cache = LocMemCache("test", {"MAX_ENTRIES": 10, "PREFIX": "test"})

    # test set and get
    await cache.set("foo", "bar")
    assert await cache.get("foo") == "bar"
    await cache.set("foo2", "baz")
    assert await cache.get("foo2") == "baz"

    # test timeout
    await cache.set("foo3", "bar", timeout=0.5)
    await asyncio.sleep(0.6)
    await cache.get("foo3") is None

    # test incr
    await cache.set("foo4", 1)
    await cache.incr("foo4")
    assert await cache.get("foo4") == 2

    # test failed incr
    with pytest.raises(ValueError):
        await cache.incr("foo5")

    # test decr
    await cache.decr("foo4")
    assert await cache.get("foo4") == 1

    # test delete
    await cache.delete("foo4")
    assert await cache.get("foo4") is None

    # test delete non-exist key
    await cache.delete("foo4") == False

    # test clear
    await cache.set("foo5", "bar")
    await cache.set("foo6", "baz")
    await cache.clear()

    assert await cache.get("foo5") is None
    assert await cache.get("foo6") is None

    # test max_entries
    for i in range(11):
        await cache.set(f"foo{i}", f"bar{i}")

    assert await cache.get("foo0") is None
