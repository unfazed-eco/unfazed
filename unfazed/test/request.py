import asyncio
import base64
import hashlib
import typing as t
import warnings
from contextlib import asynccontextmanager

import httpx
from asgiref.testing import ApplicationCommunicator
from httpx import Request, Response
from httpx._transports.asgi import ASGIResponseStream, create_event

from unfazed.type import ASGIApp, Message, Receive, Scope, Send

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


# hope httpx.ASGITransport support state one day
# refer: https://github.com/encode/httpx/discussions/3464
# no cover: start
class ASGITransport(httpx.AsyncBaseTransport):
    """
    Add state support to httpx.ASGITransport
    """

    def __init__(
        self,
        app: ASGIApp,
        state: t.Dict[str, t.Any],
        raise_app_exceptions: bool = True,
        root_path: str = "",
        client: tuple[str, int] = ("127.0.0.1", 123),
    ) -> None:
        self.app = app
        self.raise_app_exceptions = raise_app_exceptions
        self.root_path = root_path
        self.client = client
        self.state = state

    async def handle_async_request(
        self,
        request: Request,
    ) -> Response:
        assert isinstance(request.stream, httpx.AsyncByteStream)

        # ASGI scope.
        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": request.method,
            "headers": [(k.lower(), v) for (k, v) in request.headers.raw],
            "scheme": request.url.scheme,
            "path": request.url.path,
            "raw_path": request.url.raw_path.split(b"?")[0],
            "query_string": request.url.query,
            "server": (request.url.host, request.url.port),
            "client": self.client,
            "root_path": self.root_path,
            "state": self.state.copy(),
        }

        # Request.
        request_body_chunks = request.stream.__aiter__()
        request_complete = False

        # Response.
        status_code = None
        response_headers = None
        body_parts = []
        response_started = False
        response_complete = create_event()

        # ASGI callables.

        async def receive() -> dict[str, t.Any]:
            nonlocal request_complete

            if request_complete:
                await response_complete.wait()
                return {"type": "http.disconnect"}

            try:
                body = await request_body_chunks.__anext__()
            except StopAsyncIteration:
                request_complete = True
                return {"type": "http.request", "body": b"", "more_body": False}
            return {"type": "http.request", "body": body, "more_body": True}

        async def send(message: dict[str, t.Any]) -> None:
            nonlocal status_code, response_headers, response_started

            if message["type"] == "http.response.start":
                assert not response_started

                status_code = message["status"]
                response_headers = message.get("headers", [])
                response_started = True

            elif message["type"] == "http.response.body":
                assert not response_complete.is_set()
                body = message.get("body", b"")
                more_body = message.get("more_body", False)

                if body and request.method != "HEAD":
                    body_parts.append(body)

                if not more_body:
                    response_complete.set()

        try:
            await self.app(scope, t.cast(Receive, receive), t.cast(Send, send))
        except Exception:  # noqa: PIE-786
            if self.raise_app_exceptions:
                raise

            response_complete.set()
            if status_code is None:
                status_code = 500
            if response_headers is None:
                response_headers = {}

        assert response_complete.is_set()
        assert status_code is not None
        assert response_headers is not None

        stream = ASGIResponseStream(body_parts)

        return Response(status_code, headers=response_headers, stream=stream)


# no cover: stop


class Requestfactory(httpx.AsyncClient):
    """
    A test client factory for Unfazed applications that provides an easy way to test your ASGI application.

    This class extends httpx.AsyncClient and provides a convenient interface for making HTTP requests
    to your Unfazed application during testing. It handles the ASGI transport and lifespan events
    automatically.

    Features:
        - Automatic lifespan management (startup/shutdown)
        - State sharing between requests
        - Simple HTTP request methods (get, post, put, etc.)
        - ASGI transport integration

    Usage:
        ```python
        from unfazed import Unfazed
        from unfazed.test.request import Requestfactory

        async def test_your_app() -> None:
            # Initialize your Unfazed application
            unfazed = Unfazed()
            await unfazed.setup()

            # Create a test client and make requests
            async with Requestfactory(unfazed) as request:
                # Make HTTP requests using httpx.AsyncClient methods
                response = await request.get("/")
                assert response.status_code == 200
                assert response.json() == {"message": "Hello, World!"}

                # Make POST request with data
                response = await request.post("/api/data", json={"key": "value"})
                assert response.status_code == 201
        ```

    Args:
        app: The Unfazed application instance to test
        lifespan_on: Whether to handle lifespan events (startup/shutdown). Defaults to True
        base_url: The base URL for all requests. Defaults to "http://testserver"
    """

    def __init__(
        self,
        app: "Unfazed",
        lifespan_on: bool = True,
        base_url: str = "http://testserver",
    ) -> None:
        self.app = app

        self.app_state: t.Dict[str, t.Any] = {}
        transport = ASGITransport(app, self.app_state)
        scope: Scope = {
            "type": "lifespan",
            "asgi": {"version": "3.0", "spec_version": "2.1"},
            "state": self.app_state,
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
        await self.communicator.send_input(
            {"type": "lifespan.startup", "state": self.app_state}
        )  # type: ignore
        message = await self.communicator.receive_output()  # type: ignore
        if message["type"] != "lifespan.startup.complete":
            raise RuntimeError("Startup failed")

    async def lifespan_shutdown(self) -> None:
        await self.communicator.send_input({"type": "lifespan.shutdown"})  # type: ignore
        message = await self.communicator.receive_output()  # type: ignore
        if message["type"] != "lifespan.shutdown.complete":
            warnings.warn("Shutdown failed", RuntimeWarning, stacklevel=2)

    @asynccontextmanager
    async def websocket_connect(
        self, url: str, subprotocols: t.List[str] | None = None
    ) -> t.AsyncIterator["WebSocketTestSession"]:
        """Establish a WebSocket connection for testing.

        Usage:
            ```python
            async with Requestfactory(app) as client:
                async with client.websocket_connect("/ws/chat/1") as ws:
                    ws.send_text("hello")
                    response = ws.receive_text()
                    assert response == "echo: hello"
            ```
        """
        scope = self._build_websocket_scope(url, subprotocols)
        session = WebSocketTestSession(self.app, scope)
        await session._start()
        try:
            yield session
        finally:
            await session._stop()

    def _build_websocket_scope(
        self, url: str, subprotocols: t.List[str] | None = None
    ) -> Scope:
        from urllib.parse import unquote, urlparse

        parsed = urlparse(url)
        path = unquote(parsed.path)
        query_string = parsed.query.encode("utf-8")
        raw_path = path.encode("utf-8")

        headers: t.List[t.Tuple[bytes, bytes]] = [
            (b"host", b"testserver"),
            (b"connection", b"upgrade"),
            (b"upgrade", b"websocket"),
            (b"sec-websocket-version", b"13"),
            (
                b"sec-websocket-key",
                base64.b64encode(hashlib.sha1(b"test_key").digest()),
            ),
        ]

        if subprotocols:
            headers.append(
                (
                    b"sec-websocket-protocol",
                    b", ".join(s.encode() for s in subprotocols),
                )
            )

        return {
            "type": "websocket",
            "asgi": {"version": "3.0", "spec_version": "2.1"},
            "http_version": "1.1",
            "scheme": "ws",
            "path": path,
            "raw_path": raw_path,
            "query_string": query_string,
            "headers": [(k.decode(), v.decode()) for k, v in headers],
            "client": ("127.0.0.1", 50000),
            "server": ("testserver", 80),
            "subprotocols": subprotocols or [],
            "state": self.app_state.copy(),
        }


class WebSocketTestSession:
    """WebSocket test session for use with Requestfactory.websocket_connect().

    Provides methods to send and receive WebSocket messages in tests.
    Uses asyncio.Queue for message passing between the test and the ASGI app.
    """

    def __init__(self, app: ASGIApp, scope: Scope) -> None:
        self.app = app
        self.scope = scope
        self._app_queue: asyncio.Queue[Message] = asyncio.Queue()
        self._client_queue: asyncio.Queue[Message] = asyncio.Queue()
        self._app_task: asyncio.Task[None] | None = None
        self._close_message: Message | None = None

    async def _start(self) -> None:
        async def app_receive() -> Message:
            return await self._app_queue.get()

        async def app_send(message: Message) -> None:
            await self._client_queue.put(message)

        self._app_task = asyncio.create_task(
            self.app(self.scope, app_receive, app_send)  # type: ignore[arg-type]
        )

        # Send websocket.connect to initiate the connection
        await self._app_queue.put({"type": "websocket.connect"})

        # Wait for accept or close
        message = await self._client_queue.get()
        if message["type"] == "websocket.close":
            self._close_message = message
            return
        self._close_message = None
        self.accepted_subprotocol = message.get("subprotocol", None)

    async def _stop(self) -> None:
        try:
            self._app_queue.put_nowait({"type": "websocket.disconnect", "code": 1000})
        except Exception:  # pragma: no cover
            pass
        if self._app_task is not None and not self._app_task.done():
            self._app_task.cancel()
            try:
                await self._app_task
            except asyncio.CancelledError:
                pass

    async def send(self, message: Message) -> None:
        await self._app_queue.put(message)

    async def receive(self) -> Message:
        if self._close_message is not None:
            msg = self._close_message
            self._close_message = None
            return msg
        return await self._client_queue.get()

    async def send_text(self, data: str) -> None:
        await self.send({"type": "websocket.receive", "text": data})

    async def send_bytes(self, data: bytes) -> None:
        await self.send({"type": "websocket.receive", "bytes": data})

    async def send_json(self, data: t.Any) -> None:
        import orjson

        await self.send_text(orjson.dumps(data).decode())

    async def receive_text(self) -> str:
        message = await self.receive()
        assert (
            message["type"] == "websocket.send"
        ), f"Expected websocket.send, got {message['type']}"
        return t.cast(str, message["text"])

    async def receive_bytes(self) -> bytes:
        message = await self.receive()
        assert (
            message["type"] == "websocket.send"
        ), f"Expected websocket.send, got {message['type']}"
        return t.cast(bytes, message["bytes"])

    async def receive_json(self) -> t.Any:
        import orjson

        text = await self.receive_text()
        return orjson.loads(text)

    async def close(self, code: int = 1000, reason: str = "") -> None:
        await self.send({"type": "websocket.disconnect", "code": code})
