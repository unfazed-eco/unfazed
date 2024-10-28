import typing as t

from asgiref import typing as at
from starlette.middleware.base import BaseHTTPMiddleware as StarletteBaseHTTPMiddleware

from unfazed.http import HttpRequest, HttpResponse

RequestResponseEndpoint = t.Callable[[HttpRequest], t.Awaitable[HttpResponse]]


class BaseHttpMiddleware(StarletteBaseHTTPMiddleware):
    def __init__(self, app: at.ASGIApplication) -> None:
        self.app = app

    async def dispatch(
        self, request: HttpRequest, call_next: RequestResponseEndpoint
    ) -> HttpResponse:
        """
        Usage:
        async def dispatch(
            self, request: HttpRequest, call_next: RequestResponseEndpoint
        ) -> HttpResponse:
            # do something before calling the next middleware
            response = await call_next(request)
            # do something after calling the next middleware
            return response
        """
        raise NotImplementedError()  # pragma: no cover
