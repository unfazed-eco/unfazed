import asyncio
import typing as t

import pytest

from unfazed.cache import caches
from unfazed.cache.backends.locmem import LocMemCache
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_loc_cache",
    "CACHE": {
        "loc1": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "unfazed_cache1",
            "OPTIONS": {
                "MAX_ENTRIES": 10,
                "PREFIX": "unfazed_cache1",
            },
        },
        "loc2": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "unfazed_cache2",
        },
    },
}


async def test_locmem() -> None:
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(_Settings))
    await unfazed.setup()

    cache: LocMemCache = t.cast(LocMemCache, caches["loc1"])

    # test set and get
    await cache.set("foo", "bar")
    assert await cache.get("foo") == "bar"
    await cache.set("foo2", "baz")
    assert await cache.get("foo2") == "baz"

    # test timeout
    await cache.set("foo3", "bar", timeout=0.5)
    await asyncio.sleep(0.6)
    assert await cache.get("foo3") is None

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
    assert await cache.delete("foo4") is False

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

    await cache.close()

    assert cache._cache == {}


async def test_without_option() -> None:
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(_Settings))
    await unfazed.setup()

    cache = caches["loc2"]

    await cache.set("foo", "bar")
    assert await cache.get("foo") == "bar"
