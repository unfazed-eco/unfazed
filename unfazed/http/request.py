import typing as t

import orjson as json
from starlette.requests import Request

if t.TYPE_CHECKING:
    from unfazed.contrib.session.backends.base import SessionBase


class HttpRequest(Request):
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
    def session(self) -> "SessionBase":
        assert (
            "session" in self.scope
        ), "SessionMiddleware must be installed to access request.session"
        return self.scope["session"]
