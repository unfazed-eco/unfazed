import inspect
import typing as t
import warnings
from functools import wraps

from unfazed.concurrency import run_in_threadpool

from .handler import caches

P = t.ParamSpec("P")
_warned_functions: set[str] = set()


def is_bool_annotation(annotation: t.Any) -> bool:
    if annotation is bool:
        return True

    origin = t.get_origin(annotation)
    if origin is t.Literal:
        args = t.get_args(annotation)
        return all(isinstance(v, bool) for v in args)

    return False


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
        func_id = f"{func.__module__}:{func.__qualname__}"
        if func_id not in _warned_functions:
            _warned_functions.add(func_id)

            signature = inspect.signature(func)
            force_update_param = signature.parameters.get("force_update")
            has_force_update_param = force_update_param is not None
            has_var_keyword_param = any(
                param.kind is inspect.Parameter.VAR_KEYWORD
                for param in signature.parameters.values()
            )

            if (
                force_update_param
                and force_update_param.annotation is not inspect.Signature.empty
                and not is_bool_annotation(force_update_param.annotation)
            ):
                warnings.warn(
                    "Parameter 'force_update' should be annotated as bool when using @cached, "
                    "because this decorator reserves it for cache control.",
                    UserWarning,
                    stacklevel=2,
                )

            if not has_var_keyword_param and not has_force_update_param:
                warnings.warn(
                    "The decorated function does not accept `**kwargs` or `force_update`. "
                    "Passing `force_update` to force update the cache will raise TypeError.",
                    UserWarning,
                    stacklevel=2,
                )

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> t.Any:
            if args:
                warnings.warn(
                    "The cached decorator will ignore positional arguments, use keyword arguments instead.",
                    UserWarning,
                    stacklevel=2,
                )

            prefix = f"{func.__module__}:{func.__qualname__}"
            if include:
                suffix = ":".join(
                    [f"{k}_{str(v)}" for k, v in kwargs.items() if k in include]
                )

            else:
                suffix = ""

            key = f"{prefix}:{suffix}" if suffix else prefix

            force_update = kwargs.get("force_update", False)

            cache = caches[using]

            value = await cache.get(key)
            if value is not None and not force_update:
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
