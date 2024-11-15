import typing as t

import httpx
from asgiref.testing import ApplicationCommunicator
from asgiref.typing import ASGIApplication, Scope


class Requestfactory(httpx.AsyncClient):
    def __init__(
        self,
        app: ASGIApplication,
        app_state: t.Dict[str, t.Any] = {},
        lifespan_on: bool = True,
        base_url: str = "http://testserver",
    ) -> None:
        transport = httpx.ASGITransport(app)
        self.app = app
        scope: Scope = {
            "type": "lifespan",
            "asgi": {"version": "3.0"},
            "state": app_state,
        }
        self.communicator = ApplicationCommunicator(app, scope)
        self.lifespan_on = lifespan_on
        super().__init__(base_url=base_url, transport=transport)

    async def __aenter__(self) -> t.Self:
        if self.lifespan_on:
            await self.lifespan_startup()
        return self

    async def __aexit__(self, *args: t.Any) -> None:
        if self.lifespan_on:
            await self.lifespan_shutdown()

    async def lifespan_startup(self):
        await self.communicator.send_input({"type": "lifespan.startup"})
        message = await self.communicator.receive_output()
        if message["type"] != "lifespan.startup.complete":
            raise RuntimeError("Startup failed")

    async def lifespan_shutdown(self):
        await self.communicator.send_input({"type": "lifespan.shutdown"})
        message = await self.communicator.receive_output()
        if message["type"] != "lifespan.shutdown.complete":
            raise RuntimeError("Shutdown failed")
