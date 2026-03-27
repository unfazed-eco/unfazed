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
    with pytest.raises(TypeError):
        await test_func5(a=1, b=2, force_update=True)


async def test_cache_key_uses_func_name_or_qualname() -> None:
    class TestClassA:
        @cached(using="test_cache_deco", include=["name"])
        async def test_func(name: str) -> str:
            return "A"

    class TestClassB(TestClassA):
        @cached(using="test_cache_deco", include=["name"])
        async def test_func(name: str) -> str:
            return "B"

    # use name may be conflict, so use qualname to avoid it
    assert (
        f"{TestClassA.test_func.__module__}:{TestClassA.test_func.__name__}"
        == f"{TestClassB.test_func.__module__}:{TestClassB.test_func.__name__}"
    )
    assert (
        f"{TestClassA.test_func.__module__}:{TestClassA.test_func.__qualname__}"
        != f"{TestClassB.test_func.__module__}:{TestClassB.test_func.__qualname__}"
    )


async def test_cache_key_with_force_update() -> None:
    # case 1: no force_update param and no **kwargs -> invalid usage
    with pytest.warns(
        UserWarning, match="does not accept `\\*\\*kwargs` or `force_update`"
    ):

        @cached(using="test_cache_deco")
        async def f1(x: int) -> int:
            return x

    with pytest.raises(TypeError):
        await f1(x=1, force_update=True)

    # case 2: function accepts **kwargs -> force_update controls cache refresh
    f2_call_count = 0

    @cached(using="test_cache_deco", include=["x"])
    async def f2(x: int, **kwargs: t.Any) -> int:
        nonlocal f2_call_count
        f2_call_count += 1
        return f2_call_count

    assert await f2(x=1) == 1
    assert await f2(x=1) == 1
    assert await f2(x=1, force_update=True) == 2

    # case 3: function declares force_update: bool -> valid, no warning
    f4_call_count = 0

    @cached(using="test_cache_deco", include=["x"])
    async def f4(x: int, force_update: bool = False) -> int:
        nonlocal f4_call_count
        f4_call_count += 1
        return f4_call_count

    assert await f4(x=1) == 1
    assert await f4(x=1) == 1
    assert await f4(x=1, force_update=True) == 2

    # case 4: invalid force_update annotation -> warn at decoration time
    with pytest.warns(UserWarning, match="should be annotated as bool"):

        @cached(using="test_cache_deco")
        async def f5(x: int, force_update: int = 0) -> int:
            return x

    assert await f5(x=1) == 1


async def test_is_bool_annotation_with_literal() -> None:
    # Literal[True, False] -> bool annotation check passes, no warning emitted
    @cached(using="test_cache_deco", include=["x"])
    async def f_literal_bool(
        x: int, force_update: t.Literal[True, False] = False
    ) -> int:
        return x

    assert await f_literal_bool(x=10) == 10
    assert await f_literal_bool(x=10, force_update=True) == 10

    # Literal with non-bool values -> bool annotation check fails, warning emitted
    with pytest.warns(UserWarning, match="should be annotated as bool"):

        @cached(using="test_cache_deco")
        async def f_str_literal(
            x: int, force_update: t.Literal["yes", "no"] = "no"
        ) -> int:
            return x
