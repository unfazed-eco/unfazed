import typing as t
from functools import partial

from anyio.to_process import run_sync as _run_in_processpool
from anyio.to_thread import run_sync as _run_in_threadpool

P = t.ParamSpec("P")
T = t.TypeVar("T")


async def run_in_threadpool(
    func: t.Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T:
    """
    Run a function in a threadpool.

    Args:
        func: The function to run.
        *args: The arguments to pass to the function.
        **kwargs: The keyword arguments to pass to the function.

    Returns:
        The return value of the function.

    References:
        - https://anyio.readthedocs.io/en/stable/threads.html
        - https://anyio.readthedocs.io/en/stable/api.html#anyio.to_thread.run_sync
    """

    new_func = partial(func, *args, **kwargs)
    return await _run_in_threadpool(new_func)


async def run_in_processpool(
    func: t.Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T:
    """

    Run a function in a processpool.
    Args:
        func: The function to run.
        *args: The arguments to pass to the function.
        **kwargs: The keyword arguments to pass to the function.

    Returns:
        The return value of the function.

    References:
        - https://anyio.readthedocs.io/en/stable/subprocesses.html
        - https://anyio.readthedocs.io/en/stable/api.html#anyio.to_process.run_sync
    """

    new_func = partial(func, *args, **kwargs)
    return await _run_in_processpool(new_func)
