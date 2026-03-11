Unfazed Lifespan
================

Lifespan hooks let you run code when the server starts up and shuts down. Common uses include opening/closing database connections, warming caches, and releasing external resources. Unfazed follows the ASGI lifespan protocol — you subclass `BaseLifeSpan`, implement `on_startup` and/or `on_shutdown`, and register your class in settings.

## Quick Start

### 1. Create a lifespan class

```python
# myapp/lifespan.py
from unfazed.lifespan import BaseLifeSpan


class WarmCache(BaseLifeSpan):
    async def on_startup(self) -> None:
        print("Warming cache...")
        # pre-populate frequently accessed data

    async def on_shutdown(self) -> None:
        print("Flushing cache...")
```

### 2. Register it in settings

```python
# settings.py
UNFAZED_SETTINGS = {
    "PROJECT_NAME": "myproject",
    "LIFESPAN": [
        "myapp.lifespan.WarmCache",
    ],
}
```

When the server starts, `on_startup` is called. When the server stops, `on_shutdown` is called.

## Usage Guide

### Startup and Shutdown

Override one or both methods. Both are optional — the base class provides no-op defaults.

```python
from unfazed.lifespan import BaseLifeSpan


class ExternalServiceLifeSpan(BaseLifeSpan):
    async def on_startup(self) -> None:
        # runs once when the server starts
        self.client = await create_client(self.unfazed.settings)

    async def on_shutdown(self) -> None:
        # runs once when the server stops
        await self.client.close()
```

Every lifespan class receives the `Unfazed` application instance as `self.unfazed`, so you can access settings, app center, and other framework components.

### Sharing State via `request.state`

A lifespan can expose data to request handlers by overriding the `state` property. The returned dict is merged into `request.state`, making the data accessible in every endpoint:

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

State from all registered lifespan classes is merged into a single dict. If multiple lifespans define the same key, later registrations overwrite earlier ones.

### Multiple Lifespans

You can register multiple lifespan classes. They execute in registration order on startup and in the same order on shutdown:

```python
"LIFESPAN": [
    "myapp.lifespan.DatabaseInit",
    "myapp.lifespan.CacheWarm",
    "unfazed.cache.lifespan.CacheClear",
]
```

### Error Handling

If a lifespan's `on_startup` raises an exception, the error is logged and re-raised, which prevents the server from starting. The same applies to `on_shutdown` — errors are logged and propagated.

## Examples

### Database connection pool

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

### Using the built-in CacheClear

Unfazed ships with `CacheClear` which closes all cache backend connections on shutdown:

```python
"LIFESPAN": [
    "unfazed.cache.lifespan.CacheClear",
]
```

See the [Cache](cache.md) documentation for details.

## API Reference

### BaseLifeSpan

```python
class BaseLifeSpan:
    def __init__(self, unfazed: Unfazed) -> None
```

Base class for lifespan hooks. Subclass and override `on_startup` / `on_shutdown`.

**Attributes:**

- `unfazed: Unfazed` — The application instance.

**Methods:**

- `async on_startup() -> None`: Called when the server starts. No-op by default.
- `async on_shutdown() -> None`: Called when the server stops. No-op by default.

**Properties:**

- `state -> Dict[str, Any]`: Override to expose data to `request.state`. Returns `{}` by default.

### LifeSpanHandler

```python
class LifeSpanHandler
```

Internal registry that manages all lifespan components. You do not interact with it directly — the framework populates it from your `LIFESPAN` setting.

- `register(name: str, lifespan: BaseLifeSpan) -> None`: Register a component. Raises `ValueError` on duplicate names.
- `get(name: str) -> BaseLifeSpan | None`: Look up a component by its dotted path.
- `async on_startup() -> None`: Calls `on_startup` on all registered components.
- `async on_shutdown() -> None`: Calls `on_shutdown` on all registered components.
- `state -> State`: Merged state dict from all components.
- `clear() -> None`: Remove all registered components.
