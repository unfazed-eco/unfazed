import typing as t

from unfazed.cache import caches
from unfazed.cache.backends.dummy import DummyCache
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_dummy_cache",
    "CACHE": {
        "dummy1": {
            "BACKEND": "unfazed.cache.backends.dummy.DummyCache",
            "LOCATION": "unfazed_dummy1",
        },
    },
}


async def test_dummy_cache() -> None:
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(_Settings))
    await unfazed.setup()

    cache: DummyCache = t.cast(DummyCache, caches["dummy1"])

    # test get always returns default
    assert await cache.get("foo") is None
    assert await cache.get("foo", default="bar") == "bar"

    # test set is a no-op
    await cache.set("foo", "bar")
    assert await cache.get("foo") is None

    # test has_key always returns False
    assert await cache.has_key("foo") is False
    await cache.set("foo", "bar")
    assert await cache.has_key("foo") is False

    # test incr returns 0 (no-op)
    assert await cache.incr("counter") == 0

    # test decr returns 0 (no-op)
    assert await cache.decr("counter") == 0

    # test delete always returns False
    assert await cache.delete("foo") is False
    await cache.set("foo", "bar")
    assert await cache.delete("foo") is False

    # test clear is a no-op
    await cache.set("foo", "bar")
    await cache.clear()
    assert await cache.get("foo") is None

    # test proxied method (no-op)
    result = await cache.mget(["key1", "key2"])  # type: ignore[attr-defined]
    assert result is None

    result = await cache.any_unknown_method("arg1", kw="val")  # type: ignore[attr-defined]
    assert result is None

    # test close
    await cache.close()
    assert cache.closed is True
