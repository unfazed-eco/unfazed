import inspect
import typing as t
from functools import wraps

from unfazed.exception import LoginRequired, PermissionDenied
from unfazed.http import HttpRequest, HttpResponse


def login_required(func: t.Callable) -> t.Callable:
    """
    Decorator for endpoints that checks that the user is logged in, raise LoginRequired if not.

    Supports both async and sync endpoints.

    Usage:

    ```python


    @login_required
    async def my_endpoint(request: HttpRequest) -> HttpResponse:
        return HttpResponse("Hello, world!")

    @login_required
    def my_endpoint(request: HttpRequest) -> HttpResponse:
        return HttpResponse("Hello, world!")

    ```

    """

    @wraps(func)
    async def asyncwrapper(
        request: HttpRequest, *args: t.Any, **kwargs: t.Any
    ) -> HttpResponse:
        if not request.user:
            raise LoginRequired()

        return await func(request, *args, **kwargs)

    @wraps(func)
    def wrapper(request: HttpRequest, *args: t.Any, **kwargs: t.Any) -> HttpResponse:
        if not request.user:
            raise LoginRequired()

        return func(request, *args, **kwargs)

    if inspect.iscoroutinefunction(func):
        return asyncwrapper

    return wrapper


def permission_required(perm: str) -> t.Callable:
    """
    Decorator for endpoints that checks that the user has a specific permission,
    raise PermissionDenied if not.

    Supports both async and sync endpoints.

    Usage:

    ```python


    @permission_required("my_app.my_permission")
    async def my_endpoint(request: HttpRequest) -> HttpResponse:
        return HttpResponse("Hello, world!")

    ```
    """

    def decorator(func: t.Callable) -> t.Callable:
        @wraps(func)
        async def asyncwrapper(
            request: HttpRequest, *args: t.Any, **kwargs: t.Any
        ) -> HttpResponse:
            if not await request.user.has_permission(perm):
                raise PermissionDenied(f"Permission {perm} is required")

            if inspect.iscoroutinefunction(func):
                return await func(request, *args, **kwargs)
            else:
                return func(request, *args, **kwargs)

        return asyncwrapper

    return decorator
