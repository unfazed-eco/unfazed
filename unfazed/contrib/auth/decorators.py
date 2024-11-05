import inspect
import typing as t
from functools import wraps

from unfazed.exception import LoginRequired
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
