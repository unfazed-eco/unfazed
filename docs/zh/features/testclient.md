测试客户端
===========

Unfazed 提供 `Requestfactory`，一个基于 `httpx.AsyncClient` 构建的异步测试客户端。它自动处理 ASGI 传输和 lifespan 事件，因此你可以在不启动真实服务器的情况下向应用发送 HTTP 请求。

## 快速开始

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

`async with` 块在进入时调用 `lifespan_startup`，在退出时调用 `lifespan_shutdown`，与真实 ASGI 服务器的生命周期一致。

## 配置 Pytest Fixture

在实际项目中，在 `conftest.py` 中创建共享 fixture：

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

然后在测试中使用：

```python
from unfazed.core import Unfazed
from unfazed.test import Requestfactory


async def test_my_endpoint(unfazed: Unfazed) -> None:
    async with Requestfactory(unfazed) as client:
        resp = await client.get("/api/items")
        assert resp.status_code == 200
```

## 发送请求

`Requestfactory` 继承自 `httpx.AsyncClient`，因此所有标准 httpx 方法都可用：

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

## Lifespan 控制

默认情况下，`Requestfactory` 会触发 ASGI lifespan 事件。你可以禁用此行为：

```python
async with Requestfactory(unfazed, lifespan_on=False) as client:
    resp = await client.get("/")
```

当 `lifespan_on=True`（默认值）时：

- **进入**（`__aenter__`）：发送 `lifespan.startup` 并等待 `lifespan.startup.complete`。如果启动失败则抛出 `RuntimeError`。
- **退出**（`__aexit__`）：发送 `lifespan.shutdown` 并等待 `lifespan.shutdown.complete`。如果关闭失败则发出 `RuntimeWarning`。

## 状态共享

Lifespan 钩子可以填充共享状态（例如数据库连接池）。`Requestfactory` 会自动将此状态传播到每个请求作用域，因此 `request.state` 在生产环境中的行为完全一致：

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

在测试期间，`db` 键在 `request.state` 上可用，因为 `Requestfactory` 会将 lifespan 状态复制到每个 ASGI scope 中。

## API 参考

### Requestfactory

```python
class Requestfactory(httpx.AsyncClient)
```

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `app` | `Unfazed` | 必填 | Unfazed 应用实例。 |
| `lifespan_on` | `bool` | `True` | 是否运行 lifespan 启动/关闭。 |
| `base_url` | `str` | `"http://testserver"` | 预置到所有请求路径的基础 URL。 |

**方法：**

| 方法 | 描述 |
|--------|-------------|
| `async lifespan_startup()` | 发送 `lifespan.startup` 并断言 `lifespan.startup.complete`。失败时抛出 `RuntimeError`。 |
| `async lifespan_shutdown()` | 发送 `lifespan.shutdown` 并断言 `lifespan.shutdown.complete`。失败时发出 `RuntimeWarning`。 |

以及从 `httpx.AsyncClient` 继承的所有方法 — `get`、`post`、`put`、`patch`、`delete`、`options`、`head`、`request`、`stream` 等。
