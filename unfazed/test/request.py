import typing as t

import httpx
from asgiref.testing import ApplicationCommunicator
from starlette.types import Scope

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class Requestfactory(httpx.AsyncClient):
    """
    Requestfactory is a helper class that allows you test your Unfazed app

    Usage:
    ```python

    from unfazed import Unfazed
    from unfazed.test.request import Requestfactory

    async def test_your_app() -> None:

        unfazed = Unfazed()
        await unfazed.setup()

        async with Requestfactory(unfazed) as request:
            response = await request.get("/")
            assert response.status_code == 200

    """

    def __init__(
        self,
        app: "Unfazed",
        app_state: t.Dict[str, t.Any] = {},
        lifespan_on: bool = True,
        base_url: str = "http://testserver",
    ) -> None:
        transport = httpx.ASGITransport(app)
        self.app = app
        scope: Scope = {
            "type": "lifespan",
            "asgi": {"version": "3.0", "spec_version": "2.1"},
            "state": app_state,
        }
        self.communicator = ApplicationCommunicator(app, scope)  # type: ignore
        self.lifespan_on = lifespan_on
        super().__init__(base_url=base_url, transport=transport)

    async def __aenter__(self) -> t.Self:
        if self.lifespan_on:
            await self.lifespan_startup()
        return self

    async def __aexit__(self, *args: t.Any) -> None:
        if self.lifespan_on:
            await self.lifespan_shutdown()

    async def lifespan_startup(self) -> None:
        await self.communicator.send_input({"type": "lifespan.startup"})  # type: ignore
        message = await self.communicator.receive_output()  # type: ignore
        if message["type"] != "lifespan.startup.complete":
            raise RuntimeError("Startup failed")

    async def lifespan_shutdown(self) -> None:
        await self.communicator.send_input({"type": "lifespan.shutdown"})  # type: ignore
        message = await self.communicator.receive_output()  # type: ignore
        if message["type"] != "lifespan.shutdown.complete":
            raise RuntimeError("Shutdown failed")
