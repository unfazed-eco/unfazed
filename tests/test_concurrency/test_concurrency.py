import threading
import time

import pytest

from unfazed.concurrecy import run_in_processpool, run_in_threadpool


def sync_add(a: int, b: int) -> int:
    return a + b


def sync_greet(name: str, *, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"


def sync_no_args() -> str:
    return "no args"


def sync_get_thread_id() -> int:
    return threading.get_ident()


def sync_raise() -> None:
    raise ValueError("test error")


def sync_slow(seconds: float) -> str:
    time.sleep(seconds)
    return "done"


class TestRunInThreadpool:
    async def test_basic_args(self) -> None:
        result = await run_in_threadpool(sync_add, 1, 2)
        assert result == 3

    async def test_kwargs(self) -> None:
        result = await run_in_threadpool(sync_greet, "World", greeting="Hi")
        assert result == "Hi, World!"

    async def test_no_args(self) -> None:
        result = await run_in_threadpool(sync_no_args)
        assert result == "no args"

    async def test_runs_in_different_thread(self) -> None:
        main_thread_id = threading.get_ident()
        worker_thread_id = await run_in_threadpool(sync_get_thread_id)
        assert worker_thread_id != main_thread_id

    async def test_propagates_exception(self) -> None:
        with pytest.raises(ValueError, match="test error"):
            await run_in_threadpool(sync_raise)

    async def test_with_lambda(self) -> None:
        result = await run_in_threadpool(lambda x, y: x * y, 3, 4)
        assert result == 12


class TestRunInProcesspool:
    async def test_basic_args(self) -> None:
        result = await run_in_processpool(sync_add, 1, 2)
        assert result == 3

    async def test_kwargs(self) -> None:
        result = await run_in_processpool(sync_greet, "World", greeting="Hi")
        assert result == "Hi, World!"

    async def test_no_args(self) -> None:
        result = await run_in_processpool(sync_no_args)
        assert result == "no args"

    async def test_propagates_exception(self) -> None:
        with pytest.raises(ValueError, match="test error"):
            await run_in_processpool(sync_raise)

    async def test_slow_function(self) -> None:
        result = await run_in_processpool(sync_slow, 0.1)
        assert result == "done"
