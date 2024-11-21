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
            if not request.user.has_permission(perm):
                raise PermissionDenied(f"Permission {perm} is required")

            return await func(request, *args, **kwargs)

        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            if not request.user.has_permission(perm):
                raise PermissionDenied(f"Permission {perm} is required")

            return func(request, *args, **kwargs)

        if inspect.iscoroutinefunction(func):
            return asyncwrapper

        return wrapper

    return decorator


def permission_required_and(*perms: str) -> t.Callable:
    def decorator(func: t.Callable) -> t.Callable:
        @wraps(func)
        async def asyncwrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            if not all(request.user.has_permission(perm) for perm in perms):
                raise PermissionDenied(f"Permission {perms} is required")

            return await func(request, *args, **kwargs)

        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            if not all(request.user.has_permission(perm) for perm in perms):
                raise PermissionDenied(f"Permission {perms} is required")

            return func(request, *args, **kwargs)

        if inspect.iscoroutinefunction(func):
            return asyncwrapper

        return wrapper

    return decorator


def permission_required_or(*perms: str) -> t.Callable:
    def decorator(func: t.Callable) -> t.Callable:
        @wraps(func)
        async def asyncwrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            if not any(request.user.has_permission(perm) for perm in perms):
                raise PermissionDenied(f"Permission {perms} is required")

            return await func(request, *args, **kwargs)

        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            if not any(request.user.has_permission(perm) for perm in perms):
                raise PermissionDenied(f"Permission {perms} is required")

            return func(request, *args, **kwargs)

        if inspect.iscoroutinefunction(func):
            return asyncwrapper

        return wrapper

    return decorator
