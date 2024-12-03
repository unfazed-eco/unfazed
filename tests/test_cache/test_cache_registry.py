import pytest

from unfazed.cache import caches
from unfazed.cache.backends.locmem import LocMemCache
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed
from unfazed.test import Requestfactory

_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_cache",
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "unfazed_cache1",
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
                "PREFIX": "unfazed_cache1",
            },
        },
        "other": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "unfazed_cache2",
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
                "PREFIX": "unfazed_cache2",
            },
        },
    },
    "LIFESPAN": ["unfazed.cache.lifespan.CacheClear"],
}


async def test_cache_registry() -> None:
    unfazed = Unfazed(settings=UnfazedSettings(**_Settings))

    await unfazed.setup()

    default_cache = caches["default"]
    other_cache = caches["other"]

    assert default_cache.prefix == "unfazed_cache1"
    assert other_cache.prefix == "unfazed_cache2"

    assert "foo" not in caches

    # test non-exist cache
    with pytest.raises(KeyError):
        caches["non-exist"]

    # test cache close
    async with Requestfactory(unfazed):
        # trigger cacheclear lifespan
        pass


async def test_handler() -> None:
    caches["foo"] = LocMemCache("foo", {"MAX_ENTRIES": 1000})

    assert "foo" in caches
    assert "bar" not in caches

    with pytest.raises(KeyError):
        caches["bar"]

    del caches["foo"]

    assert "foo" not in caches

    await caches.close()
