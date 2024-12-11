import typing as t

import orjson as json
from starlette.requests import Request

if t.TYPE_CHECKING:
    from unfazed.contrib.auth.models import AbstractUser  # pragma: no cover
    from unfazed.contrib.session.backends.base import SessionBase  # pragma: no cover


class HttpRequest(Request):
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
