Unfazed Middleware
=================

Middleware in Unfazed wraps every request and response, forming an onion-like pipeline. Each middleware receives the raw ASGI `scope`, `receive`, and `send`, does its work, and calls the next layer. Unfazed ships with built-in middleware for error handling, CORS, GZip compression, and trusted-host validation, and you can write your own by subclassing `BaseMiddleware`.

## Quick Start

### 1. Create a middleware

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

### 2. Register it in settings

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

## Creating Custom Middleware

Subclass `BaseMiddleware` and implement the `__call__` method:

```python
from unfazed.middleware import BaseMiddleware
from unfazed.type import Receive, Scope, Send


class MyMiddleware(BaseMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # --- before request ---
        # modify scope, inspect headers, etc.

        await self.app(scope, receive, send)

        # --- after response ---
        # logging, metrics, etc.
```

Key points:

- **Always check `scope["type"]`** — middleware is called for all ASGI events (`http`, `websocket`, `lifespan`). Pass non-HTTP scopes through by calling `await self.app(scope, receive, send)`.
- **`self.app`** is the next layer in the stack (either another middleware or the router).
- The constructor receives a single `app` argument. If you need settings, read them from `unfazed.conf.settings` inside `__init__`.

### Accessing settings in a middleware

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

        # rate-limiting logic ...
        await self.app(scope, receive, send)
```

## Built-in Middleware

### CommonMiddleware — Error Handling

Catches unhandled exceptions and returns an error response. In debug mode it renders an HTML page with the full traceback and settings dump; in production it returns a plain `500 Internal Server Error`.

```python
"MIDDLEWARE": [
    "unfazed.middleware.internal.common.CommonMiddleware",
]
```

No additional settings required. It reads `DEBUG` from the project settings automatically.

### CORSMiddleware — Cross-Origin Resource Sharing

Wraps Starlette's `CORSMiddleware` and reads configuration from the `CORS` setting:

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

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ALLOW_ORIGINS` | `List[str]` | `["*"]` | Origins permitted to make requests. |
| `ALLOW_METHODS` | `List[str]` | `["*"]` | HTTP methods allowed. |
| `ALLOW_HEADERS` | `List[str]` | `[]` | Headers the client may send. |
| `ALLOW_CREDENTIALS` | `bool` | `False` | Whether to allow cookies/auth headers. |
| `ALLOW_ORIGIN_REGEX` | `str \| None` | `None` | Regex pattern for matching origins. |
| `EXPOSE_HEADERS` | `List[str]` | `[]` | Headers exposed to the browser. |
| `MAX_AGE` | `int` | `600` | Seconds the browser may cache preflight results. |

### GZipMiddleware — Response Compression

Wraps Starlette's `GZipMiddleware` and reads configuration from the `GZIP` setting:

```python
"MIDDLEWARE": [
    "unfazed.middleware.internal.gzip.GZipMiddleware",
],
"GZIP": {
    "MINIMUM_SIZE": 500,
    "COMPRESS_LEVEL": 9,
},
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `MINIMUM_SIZE` | `int` | `500` | Minimum response size in bytes before compression kicks in. |
| `COMPRESS_LEVEL` | `int` | `9` | Zlib compression level (1–9). |

### TrustedHostMiddleware — Host Header Validation

Wraps Starlette's `TrustedHostMiddleware` and reads configuration from the `TRUSTED_HOST` setting:

```python
"MIDDLEWARE": [
    "unfazed.middleware.internal.trustedhost.TrustedHostMiddleware",
],
"TRUSTED_HOST": {
    "ALLOWED_HOSTS": ["example.com", "*.example.com"],
    "WWW_REDIRECT": True,
},
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ALLOWED_HOSTS` | `List[str]` | `["*"]` | Accepted `Host` header values. Supports wildcard subdomains. |
| `WWW_REDIRECT` | `bool` | `True` | Redirect `www.` requests to the non-www host. |

## Execution Order

Middleware is applied in **reverse registration order** — the last middleware in the `MIDDLEWARE` list wraps the innermost layer (closest to the router), and the first middleware wraps the outermost layer (closest to the client).

```python
"MIDDLEWARE": [
    "myapp.middleware.A",   # outermost — runs first on request, last on response
    "myapp.middleware.B",   # middle
    "myapp.middleware.C",   # innermost — runs last on request, first on response
]
```

```
Client → A → B → C → Router → C → B → A → Client
```

A typical production setup:

```python
"MIDDLEWARE": [
    "unfazed.middleware.internal.common.CommonMiddleware",
    "unfazed.middleware.internal.cors.CORSMiddleware",
    "unfazed.middleware.internal.trustedhost.TrustedHostMiddleware",
    "myapp.middleware.AuthMiddleware",
]
```

## API Reference

### BaseMiddleware

```python
class BaseMiddleware(ABC):
    def __init__(self, app: ASGIApp) -> None
```

Abstract base class for all middleware. Subclass and implement `__call__`.

**Attributes:**

- `app: ASGIApp` — The next ASGI application in the stack.

**Methods:**

- `async __call__(scope: Scope, receive: Receive, send: Send) -> None`: *Abstract.* Process the request and call `self.app` to continue down the stack.

### CommonMiddleware

```python
class CommonMiddleware(BaseMiddleware)
```

Error-handling middleware. Catches exceptions and returns a debug HTML page (when `DEBUG=True`) or a plain 500 response (when `DEBUG=False`).

### CORSMiddleware

```python
class CORSMiddleware(StarletteCORSMiddleware)
```

CORS middleware. Reads configuration from the `CORS` setting. Raises `ValueError` if `CORS` is not set.

### GZipMiddleware

```python
class GZipMiddleware(StarletteGZipMiddleware)
```

GZip compression middleware. Reads configuration from the `GZIP` setting. Raises `ValueError` if `GZIP` is not set.

### TrustedHostMiddleware

```python
class TrustedHostMiddleware(StarletteTrustedHostMiddleware)
```

Host header validation middleware. Reads configuration from the `TRUSTED_HOST` setting. Raises `ValueError` if `TRUSTED_HOST` is not set.
