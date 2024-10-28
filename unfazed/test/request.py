import typing as t

import httpx
from asgiref.typing import ASGIApplication
from starlette.testclient import TestClient as StarletteTestClient


class Requestfactory(StarletteTestClient):
    def __init__(
        self,
        app: ASGIApplication,
        base_url: str = "http://testserver",
        raise_server_exceptions: bool = True,
        root_path: str = "",
        backend: t.Literal["asyncio", "trio"] = "asyncio",
        backend_options: dict[str, t.Any] | None = None,
        cookies: httpx._types.CookieTypes | None = None,
        headers: t.Dict[str, str] | None = None,
        follow_redirects: bool = True,
    ) -> None:
        super().__init__(
            app,
            base_url=base_url,
            raise_server_exceptions=raise_server_exceptions,
            root_path=root_path,
            backend=backend,
            backend_options=backend_options,
            cookies=cookies,
            headers=headers,
            follow_redirects=follow_redirects,
        )
