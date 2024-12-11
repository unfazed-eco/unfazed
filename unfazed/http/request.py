import typing as t

import orjson as json
from starlette.requests import Request

if t.TYPE_CHECKING:
    from unfazed.contrib.auth.models import AbstractUser  # pragma: no cover
    from unfazed.contrib.session.backends.base import SessionBase  # pragma: no cover
    from unfazed.core import Unfazed  # pragma: no cover


class HttpRequest(Request):
    """

    HttpRequest for unfazed

    Usage:

    ```python

    from unfazed.http import HttpRequest, HttpResponse

    async def my_view(request: HttpRequest):

        # get the request body as json
        body = await request.json()

        # get the request meta info
        path = request.path
        scheme = request.scheme

        # get the session and user from the request
        # you must have the session and user middleware installed
        session = request.session

        # you can also access the user
        # you must have the authentication middleware installed
        user = request.user

        # you can also access the app
        unfazed = request.unfazed
        return HttpResponse(content="Hello, world")


    ```

    """

    @t.override
    async def json(self) -> t.Dict:
        """
        use orjson to parse the request body as json
        """
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = json.loads(body)
        return self._json

    @property
    def scheme(self) -> str:
        return self.url.scheme

    @property
    def path(self) -> str:
        return self.url.path

    @property
    @t.override
    def session(self) -> "SessionBase":  # type: ignore
        if "session" not in self.scope:
            raise ValueError(
                "SessionMiddleware must be installed to access request.session"
            )

        return self.scope["session"]

    @property
    @t.override
    def user(self) -> "AbstractUser":  # type: ignore
        if "user" not in self.scope:
            raise ValueError(
                "AuthenticationMiddleware must be installed to access request.user"
            )
        return self.scope.get("user", None)

    @property
    def unfazed(self) -> "Unfazed":
        return self.scope["app"]
