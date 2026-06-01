WebSocket
=========

Unfazed 通过 `websocket()` 路由辅助函数和 `WebSocketConnection` 请求对象支持
WebSocket endpoint。它沿用 HTTP 路由的组织方式：定义 endpoint 函数，把路由放进
`patterns` 列表，并通过 `path(..., routes=...)` 或 `include()` 组合。

WebSocket 路由是 ASGI WebSocket 路由，不是 HTTP operation，因此不会出现在生成的
OpenAPI schema 中。

## 快速开始

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

客户端随后可以连接到 `/ws/chat/lobby?token=abc123`。

## 定义 WebSocket 路由

WebSocket endpoint 使用 `unfazed.route.websocket()`，而不是 `path()`：

```python
from unfazed.route import websocket

patterns = [
    websocket("/ws/echo", endpoint=echo),
    websocket("/ws/chat/{room_id}", endpoint=chat, name="chat"),
]
```

路径必须以 `/` 开头，`endpoint` 必须是函数。

WebSocket 路由也可以被组合到某个前缀下：

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

上面的例子会暴露 `/api/ws/echo`。

## Endpoint 签名

endpoint 的第一个参数应该是 `WebSocketConnection`：

```python
from unfazed.http import WebSocketConnection


async def echo(ws: WebSocketConnection) -> None:
    await ws.accept()
    data = await ws.receive_text()
    await ws.send_text(f"echo: {data}")
    await ws.close()
```

其他带类型注解的参数会从路径参数或初始 WebSocket upgrade 请求的 query string 中解析。

所有需要解析的参数都必须有类型注解。未标注类型的参数会在创建路由时抛出 `TypeError`；
`**kwargs` 会被签名解析器忽略。

### 路径参数

如果参数名匹配路由路径中的 `{name}` 占位符，Unfazed 会把该路径值传入 endpoint：

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

支持 Starlette 的路径转换器：

```python
async def user_socket(ws: WebSocketConnection, user_id: int) -> None:
    await ws.accept()
    await ws.send_json({"user_id": user_id})


patterns = [
    websocket("/ws/users/{user_id:int}", endpoint=user_socket),
]
```

也可以显式标记路径参数：

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

### Query 参数

不匹配路径占位符的参数会从 query string 中读取：

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

客户端可以连接到 `/ws/auth?token=abc123&retry=1`。

Query 值来自 upgrade 请求中的字符串标量，并按声明的类型转换，例如 `str(raw)` 或
`int(raw)`。如果某个 query 参数是可选的，给 endpoint 参数设置 Python 默认值即可。

!!! note

    WebSocket endpoint 当前支持用 `typing.Annotated[..., p.Path()]` 标记路径参数。
    Query 参数请使用普通的带类型标量参数，不要使用 `p.Query()`。

## 使用连接对象

`WebSocketConnection` 提供常用的 WebSocket 方法：

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

它也提供 Unfazed 相关属性：

| 属性 | 说明 |
|------|------|
| `scheme` | URL scheme，通常为 `ws` 或 `wss`。 |
| `session` | 来自 `SessionMiddleware` 的 session 对象。如果没有 session 中间件写入 scope，会抛出 `ValueError`。 |
| `user` | 来自认证中间件的当前用户。如果没有用户中间件写入 scope，会抛出 `ValueError`。 |
| `unfazed` | 当前 `Unfazed` 应用实例。 |

## 中间件

全局中间件会同时收到 WebSocket scope 和 HTTP scope。也可以在 WebSocket 路由上直接
配置路由级中间件：

```python
patterns = [
    websocket(
        "/ws/private",
        endpoint=private_socket,
        middlewares=["myapp.middleware.RequireWebSocketAuth"],
    ),
]
```

如果某个中间件只处理 HTTP，应该检查 `scope["type"]`，并把 WebSocket scope 继续传递
下去。通用 ASGI 中间件规则见 [Middleware](middleware.md)。

## 错误处理

如果客户端断开连接并且 endpoint 抛出 `WebSocketDisconnect`，Unfazed 会把它视为正常
断连。对于未预期异常，Unfazed 会先尝试用 `1011` 关闭连接，然后重新抛出异常，让中间件
栈可以继续观察到该异常。

应用层的关闭策略仍然应该写在 endpoint 中：

```python
async def guarded(ws: WebSocketConnection) -> None:
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=1008, reason="token required")
        return

    await ws.accept()
    await ws.send_text("connected")
```

## 测试 WebSocket

`Requestfactory` 提供 `websocket_connect()` 用于异步测试：

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

测试 session 支持 text、JSON、bytes、原始 ASGI message、关闭连接和 subprotocol：

```python
async with client.websocket_connect(
    "/ws/chat/lobby?token=abc123",
    subprotocols=["chat"],
) as ws:
    await ws.send_json({"text": "hi"})
    response = await ws.receive_json()
    assert response["room"] == "lobby"
```

## API 参考

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

创建 WebSocket 路由。`tags` 和 `app_label` 可用于路由组织，但 WebSocket 路由不会进入
OpenAPI。

### WebSocketConnection

```python
class WebSocketConnection
```

WebSocket endpoint 的第一个参数使用的连接对象。

### WebSocketDisconnect

```python
class WebSocketDisconnect(Exception)
```

当 endpoint 等待消息时客户端断开连接，会抛出该异常。异常对象提供 `code` 和 `reason`
属性。

### Requestfactory.websocket_connect()

```python
async def websocket_connect(
    url: str,
    subprotocols: list[str] | None = None,
) -> AsyncIterator[WebSocketTestSession]
```

在测试中打开 WebSocket 连接，并 yield 一个 `WebSocketTestSession`。

### WebSocketTestSession

常用辅助方法：

| 方法 | 说明 |
|------|------|
| `async send_text(data)` | 向应用发送 text 消息。 |
| `async send_json(data)` | 使用 `orjson` 序列化 JSON，并以 text 发送。 |
| `async send_bytes(data)` | 向应用发送 bytes。 |
| `async receive_text()` | 接收应用发出的 text 消息。 |
| `async receive_json()` | 接收 text 并用 `orjson` 解析为 JSON。 |
| `async receive_bytes()` | 接收应用发出的 bytes。 |
| `async receive()` | 接收原始 ASGI message。 |
| `async close(code=1000, reason="")` | 发送 WebSocket disconnect message。 |
