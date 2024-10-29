import typing as t

from unfazed.http import HttpResponse
from unfazed.http.request import HttpRequest
from unfazed.middleware import BaseHttpMiddleware


class SetSessionMiddleware(BaseHttpMiddleware):
    async def dispatch(
        self,
        request: HttpRequest,
        call_next: t.Callable[[HttpRequest], t.Awaitable[HttpResponse]],
    ) -> HttpResponse:
        request.session = "session.test"
        return await call_next(request)
