import typing as t

import pytest

from unfazed.cache import cached, caches
from unfazed.cache.backends.locmem import LocMemCache
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed


_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_disabled_cached",
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "test_disabled_default",
            "OPTIONS": {"MAX_ENTRIES": 1000},
        },
        "disabled": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "test_disabled_backend",
            "OPTIONS": {"MAX_ENTRIES": 1000},
            "DISABLED_CACHED": True,
        },
    },
}


@pytest.fixture(autouse=True)
async def setup_app() -> t.AsyncGenerator[None, None]:
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(_Settings))
    await unfazed.setup()
    yield
    caches.clear()


async def test_disabled_cached_skips_cache_for_async_func() -> None:
    """DISABLED_CACHED=True should bypass cache, calling the function every time."""
    call_count = 0

    @cached(using="disabled", include=["x"])
    async def fn(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return call_count

    assert await fn(x=1) == 1
    assert await fn(x=1) == 2  # not cached, called again


async def test_disabled_cached_skips_cache_for_sync_func() -> None:
    """DISABLED_CACHED=True should also work for sync functions."""
    call_count = 0

    @cached(using="disabled", include=["x"])
    def fn(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return call_count

    assert await fn(x=1) == 1
    assert await fn(x=1) == 2


async def test_enabled_cached_still_works() -> None:
    """Default backend (DISABLED_CACHED=False) should still cache normally."""
    call_count = 0

    @cached(using="default", include=["x"])
    async def fn(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return call_count

    assert await fn(x=1) == 1
    assert await fn(x=1) == 1  # cached, same result


async def test_disabled_cached_different_params() -> None:
    """DISABLED_CACHED=True should call function every time, even with different params."""
    call_count = 0

    @cached(using="disabled", include=["x"])
    async def fn(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return call_count

    assert await fn(x=1) == 1
    assert await fn(x=2) == 2
    assert await fn(x=1) == 3  # not cached, called again


async def test_no_disabled_cached_field_defaults_to_enabled() -> None:
    """When DISABLED_CACHED is not set in config, caching should work normally."""
    # "default" backend in _Settings has no DISABLED_CACHED field
    call_count = 0

    @cached(using="default", include=["x"])
    async def fn(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return call_count

    assert await fn(x=1) == 1
    assert await fn(x=1) == 1  # cached
    assert await fn(x=2) == 2  # different key, called again
    assert await fn(x=2) == 2  # cached


async def test_disabled_cached_when_cache_conf_not_found() -> None:
    """When using an alias not in settings.CACHE, should fall through to normal cache path."""
    caches["unlisted"] = LocMemCache(location="unlisted", options={"MAX_ENTRIES": 100})

    call_count = 0

    @cached(using="unlisted", include=["x"])
    async def fn(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return call_count

    # alias not in settings.CACHE -> cache_conf is None -> caching still works
    assert await fn(x=1) == 1
    assert await fn(x=1) == 1  # cached
