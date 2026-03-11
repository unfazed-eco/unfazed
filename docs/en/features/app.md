Unfazed App System
==================

Unfazed organizes code into **apps** — self-contained Python packages that each provide a piece of your project's functionality. Every app registers itself through a `BaseAppConfig` subclass, and the framework's `AppCenter` loads them all at startup. This modular structure keeps large projects maintainable and makes it easy to share or reuse components.

## Quick Start

### 1. Create an app

```bash
unfazed-cli startapp -n myapp
```

This generates a simple app skeleton:

```
myapp/
├── app.py
├── endpoints.py
├── models.py
├── routes.py
├── schema.py
├── serializers.py
├── settings.py
├── admin.py
└── test_all.py
```

For a more structured layout with sub-packages, use the `standard` template:

```bash
unfazed-cli startapp -n myapp -t standard
```

### 2. Write the AppConfig

Every app **must** have an `app.py` file containing an `AppConfig` class that extends `BaseAppConfig`:

```python
# myapp/app.py
from unfazed.app import BaseAppConfig


class AppConfig(BaseAppConfig):
    async def ready(self) -> None:
        pass
```

### 3. Register the app

Add the app's module path to `INSTALLED_APPS` in your project settings:

```python
# settings.py
UNFAZED_SETTINGS = {
    "PROJECT_NAME": "myproject",
    "INSTALLED_APPS": [
        "myapp",
    ],
}
```

When the server starts, Unfazed will import `myapp`, find `myapp.app.AppConfig`, and call its `ready()` hook.

## App Structure

An app is any Python package that contains an `app.py` with an `AppConfig` class. Beyond that requirement, you are free to organize files however you like. The conventional layout is:

| File / Directory | Purpose |
|------------------|---------|
| `app.py` | **Required.** Contains the `AppConfig` class. |
| `models.py` | Tortoise ORM model definitions. |
| `endpoints.py` | Request handler functions or classes. |
| `routes.py` | URL route declarations. |
| `serializers.py` | Pydantic-based serializers for request/response validation. |
| `settings.py` | App-level settings — auto-imported at startup via the wakeup mechanism. |
| `admin.py` | Admin panel registration. |
| `commands/` | Custom CLI commands (see [Command Discovery](#command-discovery)). |

## The `ready()` Hook

The `ready()` method is an async lifecycle hook called once during startup, right after the app is loaded. Use it for one-time initialization such as populating caches, registering signal handlers, or logging startup information.

```python
# myapp/app.py
from unfazed.app import BaseAppConfig


class AppConfig(BaseAppConfig):
    async def ready(self) -> None:
        print(f"{self.name} is ready")
```

The startup sequence for each app is:

1. Import the app module.
2. Import `app.py` and locate `AppConfig`.
3. Instantiate `AppConfig`.
4. Call `await app_config.ready()`.
5. Auto-import `settings.py` if it exists (wakeup mechanism).
6. Store the app in the registry.

Because `ready()` is awaited, you can perform async work (database queries, HTTP calls, etc.) inside it.

## Command Discovery

If your app has a `commands/` directory, Unfazed automatically discovers all Python files in it (excluding files that start with `_`) and registers them as CLI commands.

```
myapp/
├── app.py
└── commands/
    ├── __init__.py
    ├── import_data.py
    └── export_data.py
```

Each command file must define a `Command` class. See the [Command](command.md) documentation for details on writing custom commands.

## API Reference

### BaseAppConfig

```python
class BaseAppConfig(ABC):
    def __init__(self, unfazed: Unfazed, app_module: ModuleType) -> None
```

Abstract base class for application configuration. Subclass this and implement `ready()`.

**Properties:**

- `app_path -> Path`: Absolute filesystem path to the app's directory.
- `name -> str`: Fully qualified module name (e.g. `"myapp"`).
- `label -> str`: Module name with dots replaced by underscores (e.g. `"my_app"`).

**Methods:**

- `async ready() -> None`: *Abstract.* Called once at startup — put your initialization logic here.
- `list_command() -> List[Command]`: Discovers command files in the app's `commands/` directory.
- `has_models() -> bool`: Returns `True` if the app has a `models` submodule.
- `wakeup(filename: str) -> bool`: Imports a submodule by name; returns `True` on success, `False` if not found.
- `from_entry(entry: str, unfazed: Unfazed) -> BaseAppConfig` *(classmethod)*: Factory that loads an app from a dotted module path. Raises `ImportError`, `ModuleNotFoundError`, `AttributeError`, or `TypeError` if the entry is invalid.

### AppCenter

```python
class AppCenter:
    def __init__(self, unfazed: Unfazed, installed_apps: List[str]) -> None
```

Central registry that manages all installed apps. You typically don't interact with it directly — the framework creates one internally from your `INSTALLED_APPS` setting.

**Methods:**

- `async setup() -> None`: Loads and initializes every app in `installed_apps`. Raises `RuntimeError` if a duplicate app path is detected.
- `load_app(app_path: str) -> BaseAppConfig`: Loads a single app without calling `ready()`.

**Container operations:**

- `app_center["myapp"]` — get an app by module name (`KeyError` if missing).
- `"myapp" in app_center` — check if an app is registered.
- `for name, config in app_center` — iterate over all registered apps.
- `app_center.store` — the underlying `Dict[str, BaseAppConfig]`.
