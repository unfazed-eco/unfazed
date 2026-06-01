Test Client
===========

Unfazed provides `Requestfactory`, an async test client built on top of `httpx.AsyncClient`. It handles ASGI transport and lifespan events automatically, so you can send HTTP requests to your application without starting a real server.

## Quick Start

```python
import pytest
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed
from unfazed.http import HttpRequest, HttpResponse
from unfazed.route.routing import Route
from unfazed.test import Requestfactory


async def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(content="Hello, World!")


async def test_hello() -> None:
    unfazed = Unfazed(
        routes=[Route("/", endpoint=hello)],
        settings=UnfazedSettings(DEBUG=True),
    )
    await unfazed.setup()

    async with Requestfactory(unfazed) as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        assert resp.text == "Hello, World!"
```

The `async with` block calls `lifespan_startup` on enter and `lifespan_shutdown` on exit, matching the real ASGI server lifecycle.

## Setting Up a Pytest Fixture

For real projects, create a shared fixture in `conftest.py`:

```python
# conftest.py
import os
import sys
import typing as t

import pytest
from unfazed.core import Unfazed


@pytest.fixture(autouse=True)
async def unfazed() -> t.AsyncGenerator[Unfazed, None]:
    root_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(root_path)
    os.environ.setdefault("UNFAZED_SETTINGS_MODULE", "entry.settings")

    app = Unfazed()
    await app.setup()
    yield app
```

Then use it in your tests:

```python
from unfazed.core import Unfazed
from unfazed.test import Requestfactory


async def test_my_endpoint(unfazed: Unfazed) -> None:
    async with Requestfactory(unfazed) as client:
        resp = await client.get("/api/items")
        assert resp.status_code == 200
```

## Making Requests

`Requestfactory` extends `httpx.AsyncClient`, so all standard httpx methods are available:

```python
async with Requestfactory(unfazed) as client:
    # GET
    resp = await client.get("/items", params={"page": 1})

    # POST JSON
    resp = await client.post("/items", json={"name": "Widget"})

    # POST form data
    resp = await client.post("/upload", data={"field": "value"})

    # POST file upload
    resp = await client.post("/upload", files={"file": open("photo.jpg", "rb")})

    # PUT
    resp = await client.put("/items/1", json={"name": "Updated"})

    # DELETE
    resp = await client.delete("/items/1")

    # Custom headers
    resp = await client.get("/me", headers={"Authorization": "Bearer token"})
```

## Lifespan Control

By default, `Requestfactory` triggers ASGI lifespan events. You can disable this behaviour:

```python
async with Requestfactory(unfazed, lifespan_on=False) as client:
    resp = await client.get("/")
```

When `lifespan_on=True` (the default):

- **Enter** (`__aenter__`): Sends `lifespan.startup` and waits for `lifespan.startup.complete`. Raises `RuntimeError` if startup fails.
- **Exit** (`__aexit__`): Sends `lifespan.shutdown` and waits for `lifespan.shutdown.complete`. Emits `RuntimeWarning` if shutdown fails.

## State Sharing

Lifespan hooks can populate shared state (e.g. a database connection pool). `Requestfactory` automatically propagates this state to every request scope, so `request.state` works exactly as it does in production:

```python
from unfazed.lifespan import BaseLifeSpan


class DbPool(BaseLifeSpan):
    async def on_startup(self) -> None:
        self.state["db"] = await create_pool()

    async def on_shutdown(self) -> None:
        await self.state["db"].close()


async def get_users(request: HttpRequest) -> JsonResponse:
    db = request.state.db
    ...
```

During tests the `db` key is available on `request.state` because `Requestfactory` copies the lifespan state into each ASGI scope.

## API Reference

### Requestfactory

```python
class Requestfactory(httpx.AsyncClient)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app` | `Unfazed` | required | The Unfazed application instance. |
| `lifespan_on` | `bool` | `True` | Whether to run lifespan startup/shutdown. |
| `base_url` | `str` | `"http://testserver"` | Base URL prepended to all request paths. |

**Methods:**

| Method | Description |
|--------|-------------|
| `async lifespan_startup()` | Send `lifespan.startup` and assert `lifespan.startup.complete`. Raises `RuntimeError` on failure. |
| `async lifespan_shutdown()` | Send `lifespan.shutdown` and assert `lifespan.shutdown.complete`. Emits `RuntimeWarning` on failure. |
| `websocket_connect(url, subprotocols=None)` | Open a WebSocket test session as an async context manager. See [WebSocket](websocket.md). |

Plus all methods inherited from `httpx.AsyncClient` — `get`, `post`, `put`, `patch`, `delete`, `options`, `head`, `request`, `stream`, etc.
