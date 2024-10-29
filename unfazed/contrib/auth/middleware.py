import typing as t

from unfazed.http import HttpRequest, HttpResponse
from unfazed.middleware import BaseHttpMiddleware


class AuthSessionMiddleware(BaseHttpMiddleware):
    async def dispatch(
        self,
        request: HttpRequest,
        call_next: t.Callable[[HttpRequest], t.Awaitable[HttpResponse]],
    ) -> HttpResponse:
        return await super().dispatch(request, call_next)
