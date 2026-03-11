Unfazed 中间件
=================

Unfazed 中的中间件包裹每一个请求和响应，形成一个类似洋葱的管道。每个中间件接收原始的 ASGI `scope`、`receive` 和 `send`，完成自身的处理后调用下一层。Unfazed 内置了用于错误处理、CORS、GZip 压缩和可信主机验证的中间件，你也可以通过继承 `BaseMiddleware` 来编写自定义中间件。

## 快速开始

### 1. 创建中间件

```python
# myapp/middleware.py
from unfazed.middleware import BaseMiddleware
from unfazed.type import Receive, Scope, Send


class TimingMiddleware(BaseMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        import time
        start = time.perf_counter()
        await self.app(scope, receive, send)
        elapsed = time.perf_counter() - start
        print(f"{scope['path']} took {elapsed:.3f}s")
```

### 2. 在设置中注册

```python
# settings.py
UNFAZED_SETTINGS = {
    "PROJECT_NAME": "myproject",
    "MIDDLEWARE": [
        "unfazed.middleware.internal.common.CommonMiddleware",
        "myapp.middleware.TimingMiddleware",
    ],
}
```

## 创建自定义中间件

继承 `BaseMiddleware` 并实现 `__call__` 方法：

```python
from unfazed.middleware import BaseMiddleware
from unfazed.type import Receive, Scope, Send


class MyMiddleware(BaseMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # --- 请求前 ---
        # 修改 scope、检查头信息等

        await self.app(scope, receive, send)

        # --- 响应后 ---
        # 日志记录、指标统计等
```

关键要点：

- **始终检查 `scope["type"]`** — 中间件会被所有 ASGI 事件调用（`http`、`websocket`、`lifespan`）。对于非 HTTP scope，直接调用 `await self.app(scope, receive, send)` 传递即可。
- **`self.app`** 是栈中的下一层（可能是另一个中间件或路由器）。
- 构造函数接收一个 `app` 参数。如果需要访问配置，可以在 `__init__` 中从 `unfazed.conf.settings` 读取。

### 在中间件中访问设置

```python
from unfazed.conf import UnfazedSettings, settings
from unfazed.middleware import BaseMiddleware
from unfazed.type import ASGIApp, Receive, Scope, Send


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        unfazed_settings: UnfazedSettings = settings["UNFAZED_SETTINGS"]
        self.debug = unfazed_settings.DEBUG
        super().__init__(app)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 限流逻辑 ...
        await self.app(scope, receive, send)
```

## 内置中间件

### CommonMiddleware — 错误处理

捕获未处理的异常并返回错误响应。在调试模式下，会渲染一个包含完整堆栈跟踪和设置信息的 HTML 页面；在生产环境中，返回简单的 `500 Internal Server Error`。

```python
"MIDDLEWARE": [
    "unfazed.middleware.internal.common.CommonMiddleware",
]
```

无需额外配置。它会自动从项目设置中读取 `DEBUG`。

### CORSMiddleware — 跨域资源共享

封装了 Starlette 的 `CORSMiddleware`，从 `CORS` 设置中读取配置：

```python
"MIDDLEWARE": [
    "unfazed.middleware.internal.cors.CORSMiddleware",
],
"CORS": {
    "ALLOW_ORIGINS": ["https://example.com"],
    "ALLOW_METHODS": ["GET", "POST"],
    "ALLOW_HEADERS": ["Authorization", "Content-Type"],
    "ALLOW_CREDENTIALS": True,
    "EXPOSE_HEADERS": [],
    "MAX_AGE": 600,
},
```

| 设置项 | 类型 | 默认值 | 说明 |
|---------|------|---------|-------------|
| `ALLOW_ORIGINS` | `List[str]` | `["*"]` | 允许发起请求的源。 |
| `ALLOW_METHODS` | `List[str]` | `["*"]` | 允许的 HTTP 方法。 |
| `ALLOW_HEADERS` | `List[str]` | `[]` | 客户端可以发送的请求头。 |
| `ALLOW_CREDENTIALS` | `bool` | `False` | 是否允许携带 cookie/认证头。 |
| `ALLOW_ORIGIN_REGEX` | `str \| None` | `None` | 用于匹配源的正则表达式。 |
| `EXPOSE_HEADERS` | `List[str]` | `[]` | 暴露给浏览器的响应头。 |
| `MAX_AGE` | `int` | `600` | 浏览器缓存预检结果的秒数。 |

### GZipMiddleware — 响应压缩

封装了 Starlette 的 `GZipMiddleware`，从 `GZIP` 设置中读取配置：

```python
"MIDDLEWARE": [
    "unfazed.middleware.internal.gzip.GZipMiddleware",
],
"GZIP": {
    "MINIMUM_SIZE": 500,
    "COMPRESS_LEVEL": 9,
},
```

| 设置项 | 类型 | 默认值 | 说明 |
|---------|------|---------|-------------|
| `MINIMUM_SIZE` | `int` | `500` | 触发压缩的最小响应体大小（字节）。 |
| `COMPRESS_LEVEL` | `int` | `9` | Zlib 压缩级别（1–9）。 |

### TrustedHostMiddleware — Host 头验证

封装了 Starlette 的 `TrustedHostMiddleware`，从 `TRUSTED_HOST` 设置中读取配置：

```python
"MIDDLEWARE": [
    "unfazed.middleware.internal.trustedhost.TrustedHostMiddleware",
],
"TRUSTED_HOST": {
    "ALLOWED_HOSTS": ["example.com", "*.example.com"],
    "WWW_REDIRECT": True,
},
```

| 设置项 | 类型 | 默认值 | 说明 |
|---------|------|---------|-------------|
| `ALLOWED_HOSTS` | `List[str]` | `["*"]` | 可接受的 `Host` 头值。支持通配符子域名。 |
| `WWW_REDIRECT` | `bool` | `True` | 将 `www.` 请求重定向到非 www 主机。 |

## 执行顺序

中间件按照**注册顺序的逆序**应用 — `MIDDLEWARE` 列表中最后一个中间件包裹最内层（最靠近路由器），第一个中间件包裹最外层（最靠近客户端）。

```python
"MIDDLEWARE": [
    "myapp.middleware.A",   # 最外层 — 请求时最先执行，响应时最后执行
    "myapp.middleware.B",   # 中间层
    "myapp.middleware.C",   # 最内层 — 请求时最后执行，响应时最先执行
]
```

```
Client → A → B → C → Router → C → B → A → Client
```

典型的生产环境配置：

```python
"MIDDLEWARE": [
    "unfazed.middleware.internal.common.CommonMiddleware",
    "unfazed.middleware.internal.cors.CORSMiddleware",
    "unfazed.middleware.internal.trustedhost.TrustedHostMiddleware",
    "myapp.middleware.AuthMiddleware",
]
```

## API 参考

### BaseMiddleware

```python
class BaseMiddleware(ABC):
    def __init__(self, app: ASGIApp) -> None
```

所有中间件的抽象基类。继承此类并实现 `__call__` 方法。

**属性：**

- `app: ASGIApp` — 栈中的下一个 ASGI 应用。

**方法：**

- `async __call__(scope: Scope, receive: Receive, send: Send) -> None`：*抽象方法。* 处理请求并调用 `self.app` 继续沿栈向下传递。

### CommonMiddleware

```python
class CommonMiddleware(BaseMiddleware)
```

错误处理中间件。捕获异常并在 `DEBUG=True` 时返回调试 HTML 页面，在 `DEBUG=False` 时返回简单的 500 响应。

### CORSMiddleware

```python
class CORSMiddleware(StarletteCORSMiddleware)
```

CORS 中间件。从 `CORS` 设置中读取配置。如果未设置 `CORS`，则抛出 `ValueError`。

### GZipMiddleware

```python
class GZipMiddleware(StarletteGZipMiddleware)
```

GZip 压缩中间件。从 `GZIP` 设置中读取配置。如果未设置 `GZIP`，则抛出 `ValueError`。

### TrustedHostMiddleware

```python
class TrustedHostMiddleware(StarletteTrustedHostMiddleware)
```

Host 头验证中间件。从 `TRUSTED_HOST` 设置中读取配置。如果未设置 `TRUSTED_HOST`，则抛出 `ValueError`。
