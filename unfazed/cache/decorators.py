import inspect
import typing as t
import warnings
from functools import wraps

from unfazed.concurrecy import run_in_threadpool

from .handler import caches

P = t.ParamSpec("P")


def is_bool_annotation(annotation: t.Any) -> bool:
    if annotation is bool:
        return True

    origin = t.get_origin(annotation)
    if origin is t.Literal:
        args = t.get_args(annotation)
        return all(isinstance(v, bool) for v in args)

    return False


def resolve_signature_target(func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
    current: t.Any = func
    visited: set[int] = set()

    while callable(current):
        if inspect.ismethod(current):
            current = current.__func__

        current_id = id(current)
        if current_id in visited:
            return current
        visited.add(current_id)

        wrapped = getattr(current, "__wrapped__", None)
        if callable(wrapped):
            current = wrapped
            continue

        code = getattr(current, "__code__", None)
        closure = getattr(current, "__closure__", None)
        freevars = getattr(code, "co_freevars", ())
        if closure and freevars:
            closure_vars: dict[str, t.Any] = {}
            for name, cell in zip(freevars, closure):
                try:
                    closure_vars[name] = cell.cell_contents
                except ValueError:
                    continue

            for name in (
                "func",
                "f",
                "wrapped",
                "wrapped_func",
                "fn",
                "callable_obj",
                "inner",
            ):
                candidate = closure_vars.get(name)
                if callable(candidate):
                    current = candidate
                    break
            else:
                callable_cells = [value for value in closure_vars.values() if callable(value)]
                if len(callable_cells) == 1:
                    current = callable_cells[0]
                else:
                    return current
            continue

        return current

    return func


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
        has_force_update_param: bool | None = None
        has_var_keyword_param: bool | None = None

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> t.Any:
            nonlocal has_force_update_param, has_var_keyword_param
            if has_force_update_param is None or has_var_keyword_param is None:
                signature_target = resolve_signature_target(func)
                signature = inspect.signature(signature_target)
                force_update_param = signature.parameters.get("force_update")
                has_force_update_param = force_update_param is not None
                has_var_keyword_param = any(
                    param.kind is inspect.Parameter.VAR_KEYWORD
                    for param in signature.parameters.values()
                )

                if (
                    has_force_update_param
                    and force_update_param.annotation is not inspect.Signature.empty
                    and not is_bool_annotation(force_update_param.annotation)
                ):
                    raise TypeError(
                        "Parameter 'force_update' must be annotated as bool when using @cached, "
                        "because the decorator reserves this parameter for cache control."
                    )

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

            force_update_passed = "force_update" in kwargs
            if (
                force_update_passed
                and not has_force_update_param
                and not has_var_keyword_param
            ):
                raise TypeError(
                    "The decorated function must define `force_update: bool` or accept `**kwargs` "
                    "to use the `force_update` argument."
                )

            force_update = kwargs.get("force_update", False)
            if not isinstance(force_update, bool):
                if has_force_update_param:
                    raise TypeError(
                        "Parameter 'force_update' is reserved by @cached and cannot be overridden "
                        "with non-boolean values."
                    )
                warnings.warn(
                    "The `force_update` argument should be a boolean value. "
                    "Received non-boolean value and falling back to cached behavior.",
                    UserWarning,
                    stacklevel=2,
                )
                force_update = False
                if "force_update" in kwargs:
                    kwargs["force_update"] = force_update

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
