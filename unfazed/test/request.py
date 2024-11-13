import contextlib
import math
import typing as t

import anyio
import httpx
from anyio.abc import ObjectReceiveStream, ObjectSendStream
from anyio.streams.stapled import StapledObjectStream
from asgiref.typing import ASGIApplication


class _AsyncBackend(t.TypedDict):
    backend: str
    backend_options: dict[str, t.Any]


class Requestfactory(httpx.AsyncClient):
    def __init__(
        self,
        app: ASGIApplication,
        base_url: str = "http://testserver",
    ) -> None:
        transport = httpx.ASGITransport(app)
        self.app = app
        self.app_state: dict[str, t.Any] = {}
        self.async_backend = _AsyncBackend(backend="asyncio", backend_options={})
        super().__init__(base_url=base_url, transport=transport)

    def __enter__(self) -> t.Self:
        with contextlib.ExitStack() as stack:
            self.portal = portal = stack.enter_context(
                anyio.from_thread.start_blocking_portal(**self.async_backend)
            )

            @stack.callback
            def reset_portal() -> None:
                self.portal = None

            send1: ObjectSendStream[t.MutableMapping[str, t.Any] | None]
            receive1: ObjectReceiveStream[t.MutableMapping[str, t.Any] | None]
            send2: ObjectSendStream[t.MutableMapping[str, t.Any]]
            receive2: ObjectReceiveStream[t.MutableMapping[str, t.Any]]
            send1, receive1 = anyio.create_memory_object_stream(math.inf)
            send2, receive2 = anyio.create_memory_object_stream(math.inf)
            self.stream_send = StapledObjectStream(send1, receive1)
            self.stream_receive = StapledObjectStream(send2, receive2)
            self.task = portal.start_task_soon(self.lifespan)
            portal.call(self.wait_startup)

            @stack.callback
            def wait_shutdown() -> None:
                portal.call(self.wait_shutdown)

            self.exit_stack = stack.pop_all()

        return self

    def __exit__(self, *args: t.Any) -> None:
        self.exit_stack.close()

    async def lifespan(self) -> None:
        scope = {"type": "lifespan", "state": self.app_state}
        try:
            await self.app(scope, self.stream_receive.receive, self.stream_send.send)
        finally:
            await self.stream_send.send(None)

    async def wait_startup(self) -> None:
        await self.stream_receive.send({"type": "lifespan.startup"})

        async def receive() -> t.Any:
            message = await self.stream_send.receive()
            if message is None:
                self.task.result()
            return message

        message = await receive()
        assert message["type"] in (
            "lifespan.startup.complete",
            "lifespan.startup.failed",
        )
        if message["type"] == "lifespan.startup.failed":
            await receive()

    async def wait_shutdown(self) -> None:
        async def receive() -> t.Any:
            message = await self.stream_send.receive()
            if message is None:
                self.task.result()
            return message

        async with self.stream_send:
            await self.stream_receive.send({"type": "lifespan.shutdown"})
            message = await receive()
            assert message["type"] in (
                "lifespan.shutdown.complete",
                "lifespan.shutdown.failed",
            )
            if message["type"] == "lifespan.shutdown.failed":
                await receive()
