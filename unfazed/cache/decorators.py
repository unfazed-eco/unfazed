import inspect
import typing as t
import warnings
from functools import wraps

from starlette.concurrency import run_in_threadpool

from .handler import caches

P = t.ParamSpec("P")


def cached(
    using: str = "default",
    timeout: int = 60,
    include: t.List[str] | None = None,
) -> t.Callable:
    """
    Decorator for caching the results of async or sync functions.

    This decorator caches the return value of a function based on its arguments.
    The cache key is generated using the function's module, name, and specified parameters.

    Args:
        using (str): Name of the cache backend to use. Must be configured in settings.CACHES.
                    Defaults to "default".
        timeout (int): Time in seconds before the cache entry expires. Defaults to 60.
        include (List[str] | None): List of parameter names to include in the cache key.
                                  If None, all parameters are included. Defaults to None.

    Returns:
        Callable: A decorated async function that caches its results.

    Raises:
        KeyError: If the specified cache backend is not available.

    Examples:
        Basic usage:
        ```python
        @cached(timeout=60)
        async def get_user_info(user_id: int) -> dict:
            return {"user_id": user_id, "name": "Alice"}
        ```

        Using specific parameters for cache key:
        ```python
        @cached(timeout=60, include=["user_id"])
        async def get_user_info(user_id: int, name: str) -> dict:
            return {"user_id": user_id, "name": name}
        ```

        Using a different cache backend:
        ```python
        @cached(using="redis", timeout=60)
        async def get_user_info(user_id: int) -> dict:
            return {"user_id": user_id, "name": "Alice"}
        ```

        Force cache update:
        ```python
        # This will bypass the cache and update it with new data
        await get_user_info(user_id=1, force_update=True)
        ```

    Notes:
        - The decorator only works with keyword arguments. Positional arguments are ignored.
        - Cache keys are generated using the format: "module:function_name:param1_value:param2_value"
        - The cache can be bypassed using the `force_update=True` parameter.
    """

    def decorator(
        func: t.Callable[P, t.Awaitable[t.Any] | t.Any],
    ) -> t.Callable[P, t.Awaitable[t.Any] | t.Any]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> t.Any:
            if args:
                warnings.warn(
                    "The cached decorator will ignore positional arguments, use keyword arguments instead.",
                    UserWarning,
                    stacklevel=2,
                )

            prefix = f"{func.__module__}:{func.__name__}"
            if include:
                suffix = ":".join(
                    [f"{k}_{str(v)}" for k, v in kwargs.items() if k in include]
                )

            else:
                suffix = ""

            key = f"{prefix}:{suffix}" if suffix else prefix

            force_update = kwargs.pop("force_update", False)

            cache = caches[using]

            value = await cache.get(key)
            if value and not force_update:
                return value
            else:
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = await run_in_threadpool(func, *args, **kwargs)
                await cache.set(key, result, timeout)
                return result

        return wrapper

    return decorator
