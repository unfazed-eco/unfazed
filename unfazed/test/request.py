from __future__ import annotations

import httpx
from asgiref.typing import ASGIApplication


class Requestfactory(httpx.AsyncClient):
    def __init__(
        self,
        app: ASGIApplication,
        base_url: str = "http://testserver",
    ) -> None:
        transport = httpx.ASGITransport(app)
        super().__init__(base_url=base_url, transport=transport)
