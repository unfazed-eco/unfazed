import typing as t

from pydantic import BaseModel

from unfazed.http import HttpResponse
from unfazed.http.request import HttpRequest
from unfazed.middleware import BaseHttpMiddleware


class User(BaseModel):
    name: str


class SetUserMiddleware(BaseHttpMiddleware):
    async def dispatch(
        self,
        request: HttpRequest,
        call_next: t.Callable[[HttpRequest], t.Awaitable[HttpResponse]],
    ) -> HttpResponse:
        request.user = User(name="unfazed")
        return await call_next(request)
