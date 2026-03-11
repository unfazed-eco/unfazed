Unfazed Lifespan
================

Lifespan 钩子让你在服务器启动和关闭时执行代码。常见用途包括打开/关闭数据库连接、预热缓存和释放外部资源。Unfazed 遵循 ASGI lifespan 协议 —— 你继承 `BaseLifeSpan`，实现 `on_startup` 和/或 `on_shutdown`，并在配置中注册你的类。

## 快速开始

### 1. 创建 lifespan 类

```python
# myapp/lifespan.py
from unfazed.lifespan import BaseLifeSpan


class WarmCache(BaseLifeSpan):
    async def on_startup(self) -> None:
        print("Warming cache...")
        # 预填充常用数据

    async def on_shutdown(self) -> None:
        print("Flushing cache...")
```

### 2. 在配置中注册

```python
# settings.py
UNFAZED_SETTINGS = {
    "PROJECT_NAME": "myproject",
    "LIFESPAN": [
        "myapp.lifespan.WarmCache",
    ],
}
```

服务器启动时调用 `on_startup`，服务器停止时调用 `on_shutdown`。

## 使用指南

### 启动与关闭

重写一个或两个方法。两者都是可选的 —— 基类提供空实现。

```python
from unfazed.lifespan import BaseLifeSpan


class ExternalServiceLifeSpan(BaseLifeSpan):
    async def on_startup(self) -> None:
        # 服务器启动时执行一次
        self.client = await create_client(self.unfazed.settings)

    async def on_shutdown(self) -> None:
        # 服务器停止时执行一次
        await self.client.close()
```

每个 lifespan 类都会收到 `Unfazed` 应用实例作为 `self.unfazed`，因此可访问配置、app center 和其他框架组件。

### 通过 `request.state` 共享状态

Lifespan 可通过重写 `state` 属性向请求处理器暴露数据。返回的 dict 会合并到 `request.state`，使数据在每个 endpoint 中可访问：

```python
# myapp/lifespan.py
import typing as t

from unfazed.lifespan import BaseLifeSpan


class ConfigLoader(BaseLifeSpan):
    async def on_startup(self) -> None:
        self.feature_flags = {"dark_mode": True, "beta_api": False}

    @property
    def state(self) -> t.Dict[str, t.Any]:
        return {"feature_flags": self.feature_flags}
```

```python
# myapp/endpoints.py
from unfazed.http import HttpRequest, JsonResponse


async def get_flags(request: HttpRequest) -> JsonResponse:
    flags = request.state.feature_flags
    return JsonResponse(flags)
```

所有已注册 lifespan 类的 state 会合并为单个 dict。若多个 lifespan 定义相同键，后注册的会覆盖先注册的。

### 多个 Lifespan

可以注册多个 lifespan 类。它们按注册顺序在启动时执行，关闭时按相同顺序执行：

```python
"LIFESPAN": [
    "myapp.lifespan.DatabaseInit",
    "myapp.lifespan.CacheWarm",
    "unfazed.cache.lifespan.CacheClear",
]
```

### 错误处理

若 lifespan 的 `on_startup` 抛出异常，错误会被记录并重新抛出，从而阻止服务器启动。`on_shutdown` 同理 —— 错误会被记录并传播。

## 示例

### 数据库连接池

```python
# myapp/lifespan.py
import typing as t

from unfazed.lifespan import BaseLifeSpan


class DatabasePool(BaseLifeSpan):
    async def on_startup(self) -> None:
        from myapp.db import create_pool
        self.pool = await create_pool(self.unfazed.settings.DATABASE_URL)

    async def on_shutdown(self) -> None:
        await self.pool.close()

    @property
    def state(self) -> t.Dict[str, t.Any]:
        return {"db_pool": self.pool}
```

### 使用内置 CacheClear

Unfazed 内置 `CacheClear`，在关闭时关闭所有缓存后端连接：

```python
"LIFESPAN": [
    "unfazed.cache.lifespan.CacheClear",
]
```

详情请参阅 [Cache](cache.md) 文档。

## API 参考

### BaseLifeSpan

```python
class BaseLifeSpan:
    def __init__(self, unfazed: Unfazed) -> None
```

Lifespan 钩子的基类。继承并重写 `on_startup` / `on_shutdown`。

**属性：**

- `unfazed: Unfazed` — 应用实例。

**方法：**

- `async on_startup() -> None`：服务器启动时调用。默认无操作。
- `async on_shutdown() -> None`：服务器停止时调用。默认无操作。

**属性：**

- `state -> Dict[str, Any]`：重写以向 `request.state` 暴露数据。默认返回 `{}`。

### LifeSpanHandler

```python
class LifeSpanHandler
```

管理所有 lifespan 组件的内部注册表。通常无需直接与之交互 —— 框架根据 `LIFESPAN` 配置填充它。

- `register(name: str, lifespan: BaseLifeSpan) -> None`：注册组件。重复名称时抛出 `ValueError`。
- `get(name: str) -> BaseLifeSpan | None`：按点分路径查找组件。
- `async on_startup() -> None`：调用所有已注册组件的 `on_startup`。
- `async on_shutdown() -> None`：调用所有已注册组件的 `on_shutdown`。
- `state -> State`：所有组件合并后的 state dict。
- `clear() -> None`：移除所有已注册组件。
