import inspect
import typing as t
import warnings
from functools import wraps

from starlette.concurrency import run_in_threadpool

from .handler import caches


def cached(
    using: str = "default", timeout: int = 60, include: t.List[str] | None = None
) -> t.Callable:
    """
    Cache decorator for async function.

    Args:
        using (str): cache backend name.
        timeout (int): cache timeout.
        include (List[str]): cache key include list.

    Usage:
        ```python

        @cached(timeout=60)
        def get_user_info(user_id: int) -> dict:
            return {"user_id": user_id, "name": "Alice"}

        get_user_info(user_id=1)


        @cached(timeout=60, include=["user_id"])
        def get_user_info(user_id: int, name: str) -> dict:
            return {"user_id": user_id, "name": name}


        v1 = get_user_info(user_id=1, name="Alice")
        v2 = get_user_info(user_id=1, name="Bob")

        # v1 == v2

        @cached(using="redis", timeout=60)
        def get_user_info(user_id: int) -> dict:
            return {"user_id": user_id, "name": "Alice"}

        get_user_info(user_id=1)


        ```

    Attention:
        The cached decorator will ignore positional arguments, use keyword arguments instead.
    """

    def decorator(func: t.Callable) -> t.Callable:
        @wraps(func)
        async def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
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
