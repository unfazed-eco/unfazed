import inspect
import typing as t
from functools import wraps

from unfazed.exception import LoginRequired, PermissionDenied
from unfazed.http import HttpRequest, HttpResponse


def login_required(func: t.Callable) -> t.Callable:
    @wraps(func)
    async def asyncwrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user:
            raise LoginRequired()

        return await func(request, *args, **kwargs)

    @wraps(func)
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user:
            raise LoginRequired()

        return func(request, *args, **kwargs)

    if inspect.iscoroutinefunction(func):
        return asyncwrapper

    return wrapper


def permission_required(perm: str) -> t.Callable:
    def decorator(func: t.Callable) -> t.Callable:
        @wraps(func)
        async def asyncwrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            if not await request.user.has_permission(perm):
                raise PermissionDenied(f"Permission {perm} is required")

            if inspect.iscoroutinefunction(func):
                return await func(request, *args, **kwargs)
            else:
                return func(request, *args, **kwargs)

        return asyncwrapper

    return decorator
