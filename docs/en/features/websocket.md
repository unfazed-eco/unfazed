WebSocket
=========

Unfazed supports WebSocket endpoints through the `websocket()` route helper and
the `WebSocketConnection` request object. The API follows the same route
composition model as HTTP routes: define endpoint functions, put routes in a
`patterns` list, and compose them with `path(..., routes=...)` or `include()`.

WebSocket routes are ASGI WebSocket routes, not HTTP operations, so they are not
included in the generated OpenAPI schema.

## Quick Start

```python
# chat/endpoints.py
from unfazed.exception import WebSocketDisconnect
from unfazed.http import WebSocketConnection


async def chat(ws: WebSocketConnection, room_id: str, token: str) -> None:
    await ws.accept()
    try:
        await ws.send_json({"room": room_id, "token": token})
        while True:
            message = await ws.receive_json()
            await ws.send_json({"room": room_id, "echo": message})
    except WebSocketDisconnect:
        pass
```

```python
# chat/routes.py
from unfazed.route import websocket
from chat.endpoints import chat

patterns = [
    websocket("/ws/chat/{room_id}", endpoint=chat),
]
```

A client can then connect to `/ws/chat/lobby?token=abc123`.

## Defining WebSocket Routes

Use `unfazed.route.websocket()` instead of `path()` for WebSocket endpoints:

```python
from unfazed.route import websocket

patterns = [
    websocket("/ws/echo", endpoint=echo),
    websocket("/ws/chat/{room_id}", endpoint=chat, name="chat"),
]
```

Paths must start with `/`, and `endpoint` must be a function.

WebSocket routes can also be grouped under a prefix:

```python
from unfazed.route import path, websocket

patterns = [
    path(
        "/api",
        routes=[
            websocket("/ws/echo", endpoint=echo),
        ],
    ),
]
```

The example above exposes `/api/ws/echo`.

## Endpoint Signature

The first endpoint parameter should be a `WebSocketConnection`:

```python
from unfazed.http import WebSocketConnection


async def echo(ws: WebSocketConnection) -> None:
    await ws.accept()
    data = await ws.receive_text()
    await ws.send_text(f"echo: {data}")
    await ws.close()
```

Additional typed parameters are resolved from path parameters or from the query
string in the initial WebSocket upgrade request.

Every resolved parameter must have a type hint. Untyped parameters raise
`TypeError` when the route is created; `**kwargs` is ignored by the signature
parser.

### Path Parameters

If a parameter name matches a `{name}` placeholder in the route path, Unfazed
passes the path value into the endpoint:

```python
async def chat(ws: WebSocketConnection, room_id: str) -> None:
    await ws.accept()
    await ws.send_json({"room": room_id})
```

```python
patterns = [
    websocket("/ws/chat/{room_id}", endpoint=chat),
]
```

Starlette path convertors are supported:

```python
async def user_socket(ws: WebSocketConnection, user_id: int) -> None:
    await ws.accept()
    await ws.send_json({"user_id": user_id})


patterns = [
    websocket("/ws/users/{user_id:int}", endpoint=user_socket),
]
```

You can also mark a path parameter explicitly:

```python
import typing as t

from unfazed.route import params as p


async def chat(
    ws: WebSocketConnection,
    room_id: t.Annotated[str, p.Path()],
) -> None:
    await ws.accept()
    await ws.send_json({"room": room_id})
```

### Query Parameters

Parameters that do not match a path placeholder are read from the query string:

```python
async def auth_socket(ws: WebSocketConnection, token: str, retry: int = 0) -> None:
    await ws.accept()
    await ws.send_json({"token": token, "retry": retry})
```

```python
patterns = [
    websocket("/ws/auth", endpoint=auth_socket),
]
```

A client can connect to `/ws/auth?token=abc123&retry=1`.

Query values are scalar strings from the upgrade request and are converted with
the declared type, such as `str(raw)` or `int(raw)`. If a query parameter is
optional, give the endpoint parameter a Python default value.

!!! note

    WebSocket endpoints currently support `typing.Annotated[..., p.Path()]` for
    path parameters. For query parameters, use plain typed scalar parameters
    instead of `p.Query()`.

## Using the Connection

`WebSocketConnection` provides the usual WebSocket methods:

```python
await ws.accept()
text = await ws.receive_text()
payload = await ws.receive_json()
data = await ws.receive_bytes()

await ws.send_text("ok")
await ws.send_json({"ok": True})
await ws.send_bytes(b"ok")
await ws.close(code=1000)
```

It also exposes Unfazed-specific properties:

| Property | Description |
|----------|-------------|
| `scheme` | URL scheme, usually `ws` or `wss`. |
| `session` | Session object from `SessionMiddleware`. Raises `ValueError` if no session middleware populated the scope. |
| `user` | Current user from authentication middleware. Raises `ValueError` if no user middleware populated the scope. |
| `unfazed` | The current `Unfazed` application instance. |

## Middleware

Global middleware receives WebSocket scopes as well as HTTP scopes. Route-level
middleware can be attached directly to a WebSocket route:

```python
patterns = [
    websocket(
        "/ws/private",
        endpoint=private_socket,
        middlewares=["myapp.middleware.RequireWebSocketAuth"],
    ),
]
```

When writing middleware that should only handle HTTP, check `scope["type"]` and
pass WebSocket scopes through. See [Middleware](middleware.md) for the general
ASGI middleware rules.

## Error Handling

If the client disconnects and the endpoint raises `WebSocketDisconnect`, Unfazed
treats it as a normal disconnect. For unexpected exceptions, Unfazed tries to
close the connection with code `1011` before re-raising the exception so the
middleware stack can observe it.

Application-level close behavior still belongs in the endpoint:

```python
async def guarded(ws: WebSocketConnection) -> None:
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=1008, reason="token required")
        return

    await ws.accept()
    await ws.send_text("connected")
```

## Testing WebSockets

`Requestfactory` provides `websocket_connect()` for async tests:

```python
from unfazed.core import Unfazed
from unfazed.route import websocket
from unfazed.test import Requestfactory


async def test_echo(settings) -> None:
    app = Unfazed(
        routes=[websocket("/ws/echo", endpoint=echo)],
        settings=settings,
    )
    await app.setup()

    async with Requestfactory(app, lifespan_on=False) as client:
        async with client.websocket_connect("/ws/echo") as ws:
            await ws.send_text("hello")
            assert await ws.receive_text() == "echo: hello"
            await ws.close()
```

The test session supports text, JSON, bytes, raw ASGI messages, close, and
subprotocols:

```python
async with client.websocket_connect(
    "/ws/chat/lobby?token=abc123",
    subprotocols=["chat"],
) as ws:
    await ws.send_json({"text": "hi"})
    response = await ws.receive_json()
    assert response["room"] == "lobby"
```

## API Reference

### websocket()

```python
def websocket(
    path: str,
    *,
    endpoint: Callable,
    name: str | None = None,
    app_label: str | None = None,
    middlewares: list[str] | None = None,
    tags: list[str] | None = None,
) -> WebSocketRoute
```

Creates a WebSocket route. `tags` and `app_label` are kept for route
organization, but WebSocket routes are excluded from OpenAPI.

### WebSocketConnection

```python
class WebSocketConnection
```

Connection object used as the first parameter of WebSocket endpoints.

### WebSocketDisconnect

```python
class WebSocketDisconnect(Exception)
```

Raised when the client disconnects while the endpoint is waiting for a message.
The exception exposes `code` and `reason` attributes.

### Requestfactory.websocket_connect()

```python
async def websocket_connect(
    url: str,
    subprotocols: list[str] | None = None,
) -> AsyncIterator[WebSocketTestSession]
```

Opens a WebSocket connection for tests and yields a `WebSocketTestSession`.

### WebSocketTestSession

Common helpers:

| Method | Description |
|--------|-------------|
| `async send_text(data)` | Send a text message to the application. |
| `async send_json(data)` | Serialize JSON with `orjson` and send it as text. |
| `async send_bytes(data)` | Send bytes to the application. |
| `async receive_text()` | Receive a text message from the application. |
| `async receive_json()` | Receive text and parse it as JSON with `orjson`. |
| `async receive_bytes()` | Receive bytes from the application. |
| `async receive()` | Receive a raw ASGI message. |
| `async close(code=1000, reason="")` | Send a WebSocket disconnect message. |
