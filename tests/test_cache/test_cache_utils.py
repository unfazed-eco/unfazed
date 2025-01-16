import typing as t

import pytest

from unfazed.cache import cached, caches
from unfazed.cache.backends.locmem import LocMemCache


@pytest.fixture(autouse=True)
async def setup_cache_decorator() -> t.AsyncGenerator[None, None]:
    caches["test_cache_deco"] = LocMemCache(location="test_cache_deco")

    yield


async def test_cache_decorator() -> None:
    @cached(using="test_cache_deco")
    async def test_func(a: int, b: int) -> int:
        return a + b

    assert await test_func(a=1, b=2) == 3
    assert await test_func(a=1, b=2) == 3

    # test include
    @cached(using="test_cache_deco", include=["a"])
    async def test_func2(a: int, b: int) -> int:
        return a + b

    assert await test_func2(a=1, b=2) == 3
    assert await test_func2(a=1, b=4) == 3

    @cached(using="test_cache_deco")
    async def test_func3(a: int, b: int) -> int:
        return a + b

    with pytest.warns(UserWarning):
        assert await test_func3(1, 2) == 3

    @cached(using="test_cache_deco")
    def test_func4(a: int, b: int) -> int:
        return a + b

    assert await test_func4(a=1, b=2) == 3

    # force update

    @cached(using="test_cache_deco")
    async def test_func5(a: int, b: int) -> int:
        return a + b

    assert await test_func5(a=1, b=2) == 3
    assert await test_func5(a=1, b=2, force_update=True) == 3
